"""Conexión OPCIONAL a PostgreSQL: registro operacional de la API y usuarios de la interfaz.

- Si no existe la variable DATABASE_URL, no se hace nada y la API funciona igual (los endpoints
  de usuarios responden 503 BASE_NO_DISPONIBLE).
- Al arrancar se aplican db/01_esquema.sql y db/02_datos_iniciales.sql (idempotentes) y se
  registra en version_modelo el modelo cargado, identificado por el SHA-256 de sus pesos.
- Por cada solicitud se guarda UNA fila anónima en solicitud_inferencia (formato, tamaño, dimensiones,
  latencia, nº de ROI, modelo o error) y una fila por ROI en resultado_roi. NUNCA se guardan imágenes.
- Si la base falla, la inferencia NO se interrumpe (solo queda un aviso en el log).

DATABASE_URL de ejemplo (el nombre de la base distingue mayúsculas):
    postgresql+psycopg://postgres:CLAVE@localhost:5432/colorrectalai
"""
import logging
import os
from pathlib import Path
 
from starlette.concurrency import run_in_threadpool
 
log = logging.getLogger("colorrectalai.db")
 
_engine = None
_creado = False
_avisos = set()          # para no repetir el mismo aviso en cada solicitud
CARPETA_SQL = Path(__file__).resolve().parent.parent / "db"
ARCHIVOS_SQL = ("01_esquema.sql", "02_datos_iniciales.sql")
 
SQL_MODELO = "SELECT id_modelo FROM version_modelo WHERE sha256_pesos = :sha"
SQL_ERROR = "SELECT id_error FROM catalogo_error WHERE codigo_interno = :codigo"
SQL_CLASE = "SELECT id_clase FROM clase_deteccion WHERE nombre = :nombre"
SQL_SOLICITUD = (
    "INSERT INTO solicitud_inferencia "
    "(id_modelo, id_error, formato_archivo, tamano_bytes, ancho_px, alto_px, latencia_ms, num_roi) "
    "VALUES (:id_modelo, :id_error, :formato, :tamano, :ancho, :alto, :latencia, :num_roi) "
    "RETURNING id_solicitud"
)
SQL_ROI = (
    "INSERT INTO resultado_roi (id_solicitud, id_clase, orden, confianza, "
    "bbox_x_centro, bbox_y_centro, bbox_ancho, bbox_alto) "
    "VALUES (:id_solicitud, :id_clase, :orden, :confianza, :xc, :yc, :ancho, :alto)"
)
 
 
def _normalizar(url: str) -> str:
    # SQLAlchemy usaría psycopg2 con "postgresql://"; aquí se usa psycopg (v3).
    for prefijo in ("postgres://", "postgresql://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo):]
    return url
 
 
def obtener_engine():
    """Crea el motor la primera vez que se necesita. Devuelve None si no hay base configurada."""
    global _engine, _creado
    if _creado:
        return _engine
    _creado = True
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return None
    try:
        from sqlalchemy import create_engine
        _engine = create_engine(_normalizar(url), pool_pre_ping=True, pool_size=2, max_overflow=2,
                                connect_args={"connect_timeout": 3})
    except Exception:
        log.exception("No se pudo preparar la conexión a la base de datos "
                      "(¿instalaste sqlalchemy y psycopg? python -m pip install -r requirements.txt)")
        _engine = None
    return _engine
 
 
def reiniciar() -> None:
    """Olvida el motor actual (lo usan las pruebas)."""
    global _engine, _creado
    if _engine is not None:
        _engine.dispose()
    _engine, _creado = None, False
    _avisos.clear()
 
 
def estado() -> str:
    """'no_configurada' | 'conectada' | 'sin_conexion'  (se muestra en /api/v1/salud)."""
    engine = obtener_engine()
    if engine is None:
        return "no_configurada"
    try:
        from sqlalchemy import text
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return "conectada"
    except Exception:
        return "sin_conexion"
 
 
def _avisar_una_vez(clave: str, mensaje: str) -> None:
    if clave not in _avisos:
        _avisos.add(clave)
        log.warning(mensaje)
 
 
def _acotar(v: float, minimo: float = 0.0, maximo: float = 1.0) -> float:
    return max(minimo, min(maximo, float(v)))
 
 
def _insertar(latencia_ms, rois, error_codigo, modelo_sha256, formato, tamano_bytes, ancho, alto) -> None:
    engine = obtener_engine()
    if engine is None:
        return
    try:
        from sqlalchemy import text
        with engine.begin() as c:
            id_modelo = c.execute(text(SQL_MODELO), {"sha": modelo_sha256 or ""}).scalar()
            id_error = None
            if error_codigo:
                id_error = c.execute(text(SQL_ERROR), {"codigo": error_codigo}).scalar()
                if id_error is None:
                    _avisar_una_vez("e" + error_codigo, f"El código de error {error_codigo} no está en catalogo_error "
                                    "(revisa db/02_datos_iniciales.sql). No se registró la solicitud.")
                    return
            if id_modelo is None and id_error is None:
                _avisar_una_vez("modelo", "El modelo cargado no está en version_modelo, por eso no se registran las "
                                "solicitudes exitosas (revisa el arranque: el modelo se registra solo).")
                return
 
            id_solicitud = c.execute(text(SQL_SOLICITUD), {
                "id_modelo": id_modelo, "id_error": id_error, "formato": formato, "tamano": tamano_bytes,
                "ancho": ancho, "alto": alto, "latencia": int(round(latencia_ms)), "num_roi": len(rois),
            }).scalar()
 
            if rois:
                id_clase = c.execute(text(SQL_CLASE), {"nombre": "polipo"}).scalar()
                if id_clase is None:
                    _avisar_una_vez("clase", "Falta la clase 'polipo' en clase_deteccion; no se guardaron las ROI.")
                    return
                for orden, r in enumerate(rois):
                    c.execute(text(SQL_ROI), {
                        "id_solicitud": id_solicitud, "id_clase": id_clase, "orden": orden,
                        "confianza": _acotar(r.confianza),
                        "xc": _acotar(r.x + r.ancho / 2), "yc": _acotar(r.y + r.alto / 2),
                        "ancho": _acotar(r.ancho, 1e-6), "alto": _acotar(r.alto, 1e-6),
                    })
    except Exception as e:                       # el registro es opcional: nunca rompe la inferencia
        log.warning("No se pudo registrar la solicitud: %s", e.__class__.__name__)
 
 
async def registrar(latencia_ms, rois, error_codigo, modelo_sha256,
                    formato=None, tamano_bytes=None, ancho=None, alto=None) -> None:
    if obtener_engine() is None:
        return
    await run_in_threadpool(_insertar, latencia_ms, rois, error_codigo, modelo_sha256,
                            formato, tamano_bytes, ancho, alto)
 


# ----------------------------------------------------------------------------------------------
# Preparación de la base al arrancar
# ----------------------------------------------------------------------------------------------
SQL_MODELO_ACTIVO = """
WITH exp AS (
    INSERT INTO experimento (id_investigador, id_particion, nombre, entorno, framework, fecha_inicio, estado)
    SELECT i.id_investigador, p.id_particion, CAST(:nombre_exp AS VARCHAR(80)), 'Google Colab (GPU)', 'Ultralytics YOLO (ONNX)',
           CURRENT_TIMESTAMP, 'finalizado'
    FROM investigador i, particion_dataset p
    WHERE i.nombre_completo = 'Equipo System Force' AND p.nombre = 'centros_C1-C4_C5_C6'
      AND NOT EXISTS (SELECT 1 FROM version_modelo WHERE sha256_pesos = CAST(:sha AS CHAR(64)))
      AND NOT EXISTS (SELECT 1 FROM experimento WHERE nombre = CAST(:nombre_exp AS VARCHAR(80)))
    RETURNING id_experimento
)
INSERT INTO version_modelo (id_experimento, nombre, version, formato, sha256_pesos, url_release,
                            fecha_publicacion, estado)
SELECT COALESCE((SELECT id_experimento FROM exp),
                (SELECT id_experimento FROM experimento WHERE nombre = CAST(:nombre_exp AS VARCHAR(80)))),
       'ColorrectalAI YOLO', CAST(:version AS VARCHAR(20)), 'onnx', CAST(:sha AS CHAR(64)), CAST(:url AS VARCHAR(255)), CURRENT_TIMESTAMP, 'activo'
WHERE NOT EXISTS (SELECT 1 FROM version_modelo WHERE sha256_pesos = CAST(:sha AS CHAR(64)))
"""


def preparar(modelo_sha256: str, version: str, url_modelo: str = "") -> bool:
    """Aplica el esquema y los datos iniciales y deja como 'activo' el modelo cargado.

    Es idempotente y nunca lanza excepciones: devuelve False si no hay base o algo falla.
    """
    engine = obtener_engine()
    if engine is None:
        return False
    try:
        from sqlalchemy import text
        with engine.begin() as c:
            # Un solo proceso aplica las migraciones a la vez (por si hay varias réplicas).
            c.execute(text("SELECT pg_advisory_xact_lock(4242)"))
            for nombre in ARCHIVOS_SQL:
                c.exec_driver_sql((CARPETA_SQL / nombre).read_text(encoding="utf-8")
                                  .replace("BEGIN;", "").replace("COMMIT;", ""))
            if modelo_sha256 and len(modelo_sha256) == 64:
                otro = c.execute(text("SELECT sha256_pesos FROM version_modelo "
                                      "WHERE nombre = 'ColorrectalAI YOLO' AND version = :v"),
                                 {"v": version[:20]}).scalar()
                if otro and otro != modelo_sha256:   # misma versión con otros pesos: se distingue por el SHA
                    version = f"{version[:12]}-{modelo_sha256[:7]}"
                url = url_modelo or "https://github.com/colorrectalai/ColorrectalAI-proyect/tree/develop/backend/modelos"
                c.execute(text("UPDATE version_modelo SET estado = 'retirado' "
                               "WHERE estado = 'activo' AND sha256_pesos <> :sha"), {"sha": modelo_sha256})
                c.execute(text(SQL_MODELO_ACTIVO), {"sha": modelo_sha256, "version": version[:20], "url": url[:255],
                                                    "nombre_exp": f"modelo desplegado {version}"[:80]})
                c.execute(text("UPDATE version_modelo SET estado = 'activo' WHERE sha256_pesos = :sha"),
                          {"sha": modelo_sha256})
        log.info("Base de datos lista (esquema, datos iniciales y modelo %s registrados).", version)
        return True
    except Exception:
        log.exception("No se pudo preparar la base de datos; la API sigue funcionando sin registro.")
        return False
