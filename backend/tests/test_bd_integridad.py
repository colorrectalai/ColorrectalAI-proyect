"""Base de datos: restricciones, cascadas, vistas, datos iniciales, inyección, concurrencia,
transacciones y resiliencia ante una base caída.

Las pruebas de integración necesitan PostgreSQL (TEST_DATABASE_URL); sin él se saltan.
"""
import threading

import pytest
from fastapi.testclient import TestClient

from api import db
from api.main import crear_app
from ia.config import Config
from tests.conftest import ModeloFalso, png_bytes
from tests.test_usuarios_bd import SHA_FALSO, cliente_bd, requiere_bd  # noqa: F401 (fixture)


def ejecutar(sql, params=None):
    from sqlalchemy import text
    with db.obtener_engine().begin() as c:
        r = c.execute(text(sql), params or {})
        return r.all() if r.returns_rows else None


def falla(sql, params=None):
    from sqlalchemy.exc import DBAPIError
    with pytest.raises(DBAPIError):
        ejecutar(sql, params)


def id_modelo():
    return ejecutar("SELECT id_modelo FROM version_modelo WHERE estado='activo'")[0][0]


SOL = ("INSERT INTO solicitud_inferencia (id_modelo, id_error, formato_archivo, tamano_bytes, ancho_px, alto_px,"
       " latencia_ms, num_roi) VALUES (:m, :e, 'png', :t, :w, :h, :l, 0) RETURNING id_solicitud")


# ---------------- Restricciones (CHECK, UNIQUE, NOT NULL) ----------------
@requiere_bd
@pytest.mark.parametrize("campo,valor", [("t", -1), ("w", 0), ("h", -5), ("l", -1)],
                         ids=["tamano_negativo", "ancho_cero", "alto_negativo", "latencia_negativa"])
def test_solicitud_rechaza_valores_fuera_de_rango(cliente_bd, campo, valor):
    p = {"m": id_modelo(), "e": None, "t": 10, "w": 10, "h": 10, "l": 5}
    p[campo] = valor
    falla(SOL, p)


@requiere_bd
def test_solicitud_sin_modelo_ni_error_se_rechaza(cliente_bd):
    falla(SOL, {"m": None, "e": None, "t": 1, "w": 1, "h": 1, "l": 1})


@requiere_bd
@pytest.mark.parametrize("columna,valor", [("confianza", 1.5), ("confianza", -0.1), ("bbox_x_centro", 1.2),
                                           ("bbox_ancho", 0), ("bbox_alto", 1.01), ("orden", -1)])
def test_resultado_roi_rechaza_valores_invalidos(cliente_bd, columna, valor):
    sid = ejecutar(SOL, {"m": id_modelo(), "e": None, "t": 1, "w": 1, "h": 1, "l": 1})[0][0]
    clase = ejecutar("SELECT id_clase FROM clase_deteccion WHERE nombre='polipo'")[0][0]
    v = {"orden": 0, "confianza": 0.5, "bbox_x_centro": 0.5, "bbox_y_centro": 0.5, "bbox_ancho": 0.2, "bbox_alto": 0.2}
    v[columna] = valor
    falla("INSERT INTO resultado_roi (id_solicitud, id_clase, orden, confianza, bbox_x_centro, bbox_y_centro,"
          " bbox_ancho, bbox_alto) VALUES (:s, :c, :orden, :confianza, :bbox_x_centro, :bbox_y_centro,"
          " :bbox_ancho, :bbox_alto)", {"s": sid, "c": clase, **v})


@requiere_bd
def test_correo_en_mayusculas_se_rechaza_en_la_base(cliente_bd):
    falla("INSERT INTO usuario (correo, nombre_completo, hash_contrasena, acepto_aviso_en)"
          " VALUES ('ANA@X.CO', 'Ana', 'h', now())")


@requiere_bd
def test_correo_duplicado_se_rechaza_en_la_base(cliente_bd):
    q = ("INSERT INTO usuario (correo, nombre_completo, hash_contrasena, acepto_aviso_en)"
         " VALUES ('dup@x.co', 'Ana', 'h', now())")
    ejecutar(q)
    falla(q)


@requiere_bd
def test_solo_puede_haber_un_modelo_activo(cliente_bd):
    falla("INSERT INTO version_modelo (id_experimento, nombre, version, formato, sha256_pesos, url_release,"
          " fecha_publicacion, estado) SELECT id_experimento, 'Otro', 'x', 'onnx', :sha, 'u', now(), 'activo'"
          " FROM experimento LIMIT 1", {"sha": "c" * 64})


@requiere_bd
@pytest.mark.parametrize("tabla,sql", [
    ("version_modelo", "UPDATE version_modelo SET formato='exe'"),
    ("version_modelo", "UPDATE version_modelo SET estado='borrado'"),
    ("particion_dataset", "UPDATE particion_dataset SET criterio='aleatorio'"),
    ("experimento", "UPDATE experimento SET estado='raro'"),
    ("catalogo_error", "UPDATE catalogo_error SET codigo_http=200"),
    ("evaluacion", "UPDATE evaluacion SET umbral_confianza=2"),
])
def test_checks_de_dominio(cliente_bd, tabla, sql):
    falla(sql)


@requiere_bd
def test_clave_foranea_inexistente_se_rechaza(cliente_bd):
    falla(SOL, {"m": 999999, "e": None, "t": 1, "w": 1, "h": 1, "l": 1})


# ---------------- Cascadas, vistas y datos iniciales ----------------
@requiere_bd
def test_borrar_una_solicitud_borra_sus_roi(cliente_bd):
    cliente_bd.post("/api/v1/inferencias", files={"imagen": ("a.png", png_bytes(), "image/png")})
    assert ejecutar("SELECT count(*) FROM resultado_roi")[0][0] == 1
    ejecutar("DELETE FROM solicitud_inferencia")
    assert ejecutar("SELECT count(*) FROM resultado_roi")[0][0] == 0


@requiere_bd
def test_vistas_de_consulta_calculan_bien(cliente_bd):
    for _ in range(3):
        cliente_bd.post("/api/v1/inferencias", files={"imagen": ("a.png", png_bytes(), "image/png")})
    cliente_bd.post("/api/v1/inferencias", files={"imagen": ("v.png", b"", "image/png")})
    total, rois = ejecutar("SELECT total_solicitudes, total_roi FROM v_servicio_diario")[0]
    assert (total, rois) == (4, 3)
    assert ejecutar("SELECT total_errores FROM v_errores_por_tipo WHERE codigo_interno='ARCHIVO_VACIO'")[0][0] == 1


@requiere_bd
@pytest.mark.parametrize("tabla,cantidad", [("catalogo_error", 13), ("metrica", 14), ("centro_origen", 6),
                                            ("clase_deteccion", 1), ("dataset", 1), ("particion_dataset", 1)])
def test_datos_iniciales(cliente_bd, tabla, cantidad):
    assert ejecutar(f"SELECT count(*) FROM {tabla}")[0][0] == cantidad


@requiere_bd
def test_catalogo_de_errores_coincide_con_los_codigos_de_la_api(cliente_bd):
    import pathlib
    import re
    fuente = "".join(p.read_text() for p in pathlib.Path("api").glob("*.py"))
    codigos_api = set(re.findall(r'ErrorAPI\(\d+, "([A-Z_]+)"', fuente)) | {"SOLICITUD_INVALIDA", "ERROR_INTERNO",
                                                                              "RUTA_NO_ENCONTRADA", "METODO_NO_PERMITIDO",
                                                                              "ERROR_HTTP"}
    codigos_api -= {"BASE_NO_DISPONIBLE", "CORREO_REGISTRADO", "CREDENCIALES_INVALIDAS", "SESION_INVALIDA",
                    "DATOS_INVALIDOS"}       # errores de usuarios: no se registran como solicitudes de inferencia
    catalogo = {r[0] for r in ejecutar("SELECT codigo_interno FROM catalogo_error")}
    assert codigos_api <= catalogo


# ---------------- Inyección SQL y XSS ----------------
@requiere_bd
@pytest.mark.parametrize("nombre", ["Robert'); DROP TABLE usuario;--", "<script>alert('x')</script>",
                                    "' OR '1'='1", "Ana \"comillas\" ; DELETE"])
def test_nombre_malicioso_se_guarda_literal_y_no_se_ejecuta(cliente_bd, nombre):
    r = cliente_bd.post("/api/v1/usuarios", json={"nombre": nombre, "correo": "x@x.co",
                                                  "contrasena": "ClaveSegura123", "acepta_aviso": True})
    assert r.status_code == 201 and r.json()["usuario"]["nombre"] == nombre
    assert ejecutar("SELECT count(*) FROM usuario")[0][0] == 1          # la tabla sigue existiendo
    assert ejecutar("SELECT nombre_completo FROM usuario")[0][0] == nombre


@requiere_bd
@pytest.mark.parametrize("correo", ["' OR 1=1 --@x.co", "a@x.co' OR '1'='1", "admin'--@x.co"])
def test_login_con_inyeccion_en_el_correo_no_entra(cliente_bd, correo):
    cliente_bd.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "ana@x.co",
                                              "contrasena": "ClaveSegura123", "acepta_aviso": True})
    r = cliente_bd.post("/api/v1/sesiones", json={"correo": correo, "contrasena": "x' OR '1'='1"})
    assert r.status_code == 401


# ---------------- Concurrencia y transacciones ----------------
@requiere_bd
def test_registros_simultaneos_con_el_mismo_correo_crean_una_sola_cuenta(cliente_bd):
    codigos = []

    def registrar():
        r = cliente_bd.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "carrera@x.co",
                                                      "contrasena": "ClaveSegura123", "acepta_aviso": True})
        codigos.append(r.status_code)
    hilos = [threading.Thread(target=registrar) for _ in range(6)]
    [h.start() for h in hilos]; [h.join() for h in hilos]
    assert sorted(codigos).count(201) == 1 and codigos.count(409) == 5
    assert ejecutar("SELECT count(*) FROM usuario WHERE correo='carrera@x.co'")[0][0] == 1


@requiere_bd
def test_registro_operacional_es_atomico(cliente_bd, monkeypatch):
    """Si falla una ROI a mitad de la transacción, no queda la solicitud a medias."""
    from api.esquemas import ROI
    rois = [ROI(x=0.1, y=0.1, ancho=0.2, alto=0.2, confianza=0.9), ROI(x=0.1, y=0.1, ancho=0.2, alto=0.2, confianza=0.9)]
    monkeypatch.setattr(db, "SQL_ROI", db.SQL_ROI.replace(":orden", "0"))    # 2.ª ROI choca con UNIQUE(solicitud, orden)
    db._insertar(10, rois, None, SHA_FALSO, "png", 10, 10, 10)
    assert ejecutar("SELECT count(*) FROM solicitud_inferencia")[0][0] == 0
    assert ejecutar("SELECT count(*) FROM resultado_roi")[0][0] == 0


@requiere_bd
def test_ultimo_acceso_se_actualiza_al_iniciar_sesion(cliente_bd):
    cliente_bd.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "t@x.co",
                                              "contrasena": "ClaveSegura123", "acepta_aviso": True})
    ejecutar("UPDATE usuario SET ultimo_acceso = now() - interval '1 day'")
    cliente_bd.post("/api/v1/sesiones", json={"correo": "t@x.co", "contrasena": "ClaveSegura123"})
    assert ejecutar("SELECT ultimo_acceso > now() - interval '1 minute' FROM usuario")[0][0]


@requiere_bd
def test_usuario_desactivado_no_puede_entrar_ni_usar_su_token(cliente_bd):
    r = cliente_bd.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "off@x.co",
                                                  "contrasena": "ClaveSegura123", "acepta_aviso": True})
    token = r.json()["token"]
    ejecutar("UPDATE usuario SET activo = false")
    assert cliente_bd.post("/api/v1/sesiones", json={"correo": "off@x.co", "contrasena": "ClaveSegura123"}).status_code == 401
    assert cliente_bd.get("/api/v1/usuarios/yo", headers={"Authorization": "Bearer " + token}).status_code == 401


@requiere_bd
def test_token_de_usuario_borrado_no_sirve(cliente_bd):
    r = cliente_bd.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "del@x.co",
                                                  "contrasena": "ClaveSegura123", "acepta_aviso": True})
    ejecutar("DELETE FROM usuario")
    assert cliente_bd.get("/api/v1/usuarios/yo", headers={"Authorization": "Bearer " + r.json()["token"]}).status_code == 401


@requiere_bd
@pytest.mark.parametrize("limite,campo,ok", [(120, "nombre", True), (121, "nombre", False),
                                             (128, "contrasena", True), (129, "contrasena", False)])
def test_limites_exactos_del_registro(cliente_bd, limite, campo, ok):
    datos = {"nombre": "Ana", "correo": "lim@x.co", "contrasena": "ClaveSegura123", "acepta_aviso": True}
    datos[campo] = "a" * limite
    r = cliente_bd.post("/api/v1/usuarios", json=datos)
    assert r.status_code == (201 if ok else 422)


# ---------------- Resiliencia: base caída o inaccesible ----------------
@pytest.fixture
def cliente_base_caida(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://nadie:x@127.0.0.1:1/nada")   # puerto cerrado
    db.reiniciar()
    with TestClient(crear_app(Config(), ModeloFalso())) as c:
        yield c
    db.reiniciar()


def test_base_caida_salud_informa_sin_conexion(cliente_base_caida):
    assert cliente_base_caida.get("/api/v1/salud").json()["base_datos"] == "sin_conexion"


def test_base_caida_la_inferencia_sigue_funcionando(cliente_base_caida):
    r = cliente_base_caida.post("/api/v1/inferencias", files={"imagen": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 200 and r.json()["rois"]


@pytest.mark.parametrize("ruta,cuerpo", [
    ("/api/v1/usuarios", {"nombre": "Ana", "correo": "a@x.co", "contrasena": "ClaveSegura123", "acepta_aviso": True}),
    ("/api/v1/sesiones", {"correo": "a@x.co", "contrasena": "ClaveSegura123"})])
def test_base_caida_usuarios_responde_503_claro(cliente_base_caida, ruta, cuerpo):
    r = cliente_base_caida.post(ruta, json=cuerpo)
    assert r.status_code == 503 and r.json()["error"]["codigo"] == "BASE_NO_DISPONIBLE"


def test_base_caida_preparar_no_lanza(cliente_base_caida):
    assert db.preparar("a" * 64, "x") is False


def test_registrar_nunca_rompe_aunque_la_base_falle(monkeypatch):
    class MotorRoto:
        def begin(self):
            raise RuntimeError("la base se cayó a mitad")
    monkeypatch.setattr(db, "obtener_engine", lambda: MotorRoto())
    db._insertar(1, [], None, "x", "png", 1, 1, 1)          # no debe lanzar


@pytest.mark.parametrize("url,esperada", [
    ("postgres://u:p@h/d", "postgresql+psycopg://u:p@h/d"),
    ("postgresql://u:p@h/d", "postgresql+psycopg://u:p@h/d"),
    ("postgresql+psycopg://u:p@h/d", "postgresql+psycopg://u:p@h/d")])
def test_normaliza_la_url_de_railway(url, esperada):
    assert db._normalizar(url) == esperada


@pytest.mark.parametrize("v,esperado", [(-0.5, 0.0), (0.3, 0.3), (1.7, 1.0)])
def test_acotar_valores_al_rango(v, esperado):
    assert db._acotar(v) == esperado
