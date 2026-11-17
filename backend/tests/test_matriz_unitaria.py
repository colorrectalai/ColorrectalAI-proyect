"""Pruebas unitarias de la Matriz de Pruebas Unitarias de ColorrectalAI (actividad C-21).

Cada prueba lleva el ID del caso CPU-xxx de la matriz. Complementan test_api.py y test_ia.py;
los casos CPU-007, 035, 037, 038 y 045 los cubren pruebas de test_api.py."""
import asyncio
import io
import json
import os
import tempfile

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api import db
from api.admision import Admision
from api.errores import ErrorAPI, manejar_error_interno
from api.main import crear_app
from api.servicio_inferencia import analizar
from api.validacion import validar_imagen
from ia.adaptador_yolo import sha256_archivo
from ia.config import Config
from ia.explicabilidad import superponer_roi
from ia.posprocesamiento import Caja, _iou, a_imagen_original, decodificar, nms, posprocesar
from ia.preprocesamiento import preprocesar


class ModeloFalso:
    listo = True
    tamano_entrada = 640
    sha256_real = "falso"

    def __init__(self, filas=None):
        self.filas = filas or []

    def cargar(self):
        pass

    def ejecutar(self, tensor):
        s = np.zeros((1, 300, 6), dtype=np.float32)
        for i, f in enumerate(self.filas):
            s[0, i] = f
        return s


def img_bytes(ancho=800, alto=600, formato="PNG", ruido=False):
    if ruido:
        arr = np.random.default_rng(0).integers(0, 256, (alto, ancho, 3), dtype=np.uint8)
        im = Image.fromarray(arr)
    else:
        im = Image.new("RGB", (ancho, alto), (180, 80, 80))
    buf = io.BytesIO()
    im.save(buf, format=formato)
    return buf.getvalue()


CFG = Config()


def _codigo(fn):
    with pytest.raises(ErrorAPI) as e:
        fn()
    return e.value


# ---------------- Validación de archivos (api/validacion.py) ----------------
def test_CPU_001_png_valido_se_acepta():
    assert validar_imagen(img_bytes(), CFG).format == "PNG"


def test_CPU_002_jpeg_valido_se_acepta():
    assert validar_imagen(img_bytes(formato="JPEG"), CFG).format == "JPEG"


def test_CPU_003_archivo_vacio_400():
    e = _codigo(lambda: validar_imagen(b"", CFG))
    assert e.estado == 400 and e.codigo == "ARCHIVO_VACIO"


def test_CPU_004_contenido_no_imagen_415():
    e = _codigo(lambda: validar_imagen(b"%PDF-1.4 no es imagen", CFG))
    assert e.estado == 415 and e.codigo == "ARCHIVO_INVALIDO"


def test_CPU_005_formato_bmp_no_admitido_415():
    e = _codigo(lambda: validar_imagen(img_bytes(formato="BMP"), CFG))
    assert e.estado == 415 and e.codigo == "FORMATO_NO_ADMITIDO"


def test_CPU_006_imagen_de_9mb_aceptada_segun_rnf_015_2():
    # RNF-015.2: se admiten imágenes de hasta 10 MB.
    datos = img_bytes(1800, 1750, ruido=True)
    assert 8 * 1024 * 1024 < len(datos) <= 10 * 1024 * 1024
    validar_imagen(datos, CFG)


def test_CPU_008_lado_mayor_a_6000_px_422():
    e = _codigo(lambda: validar_imagen(img_bytes(6100, 40), CFG))
    assert e.estado == 422 and e.codigo == "IMAGEN_DEMASIADO_GRANDE"


def test_CPU_009_lado_menor_a_32_px_422():
    e = _codigo(lambda: validar_imagen(img_bytes(20, 20), CFG))
    assert e.estado == 422 and e.codigo == "IMAGEN_DEMASIADO_PEQUENA"


# ---------------- Preprocesamiento (ia/preprocesamiento.py) ----------------
def test_CPU_011_letterbox_imagen_vertical():
    p = preprocesar(Image.new("RGB", (600, 800)), 640)
    assert p.tensor.shape == (1, 3, 640, 640)
    assert p.escala == 0.8 and p.pad_x == 80 and p.pad_y == 0


def test_CPU_012_normalizacion_rango_0_1_y_relleno_gris():
    p = preprocesar(Image.new("RGB", (800, 600), (255, 255, 255)), 640)
    assert p.tensor.min() >= 0.0 and p.tensor.max() <= 1.0
    assert abs(p.tensor[0, 0, 0, 0] - 114 / 255) < 1e-6      # relleno
    assert abs(p.tensor[0, 0, 320, 320] - 1.0) < 1e-6        # contenido


def test_CPU_013_imagen_en_escala_de_grises_se_convierte_a_rgb():
    p = preprocesar(Image.new("L", (640, 640), 128), 640)
    assert p.tensor.shape[1] == 3


# ---------------- Posprocesamiento (ia/posprocesamiento.py) ----------------
def test_CPU_014_iou_cajas_iguales_y_disjuntas():
    a = np.array([0, 0, 10, 10], dtype=np.float32)
    b = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], dtype=np.float32)
    r = _iou(a, b)
    assert abs(r[0] - 1.0) < 1e-6 and r[1] == 0


def test_CPU_015_nms_suprime_solapadas_y_conserva_la_mas_confiable():
    cajas = np.array([[0, 0, 10, 10], [1, 1, 11, 11], [50, 50, 60, 60]], dtype=np.float32)
    scores = np.array([0.6, 0.9, 0.5], dtype=np.float32)
    assert nms(cajas, scores, 0.45) == [1, 2]


def test_CPU_017_formato_end_to_end_respeta_umbral():
    s = np.zeros((1, 300, 6), dtype=np.float32)
    s[0, 0] = [10, 10, 50, 50, 0.25, 0]       # exactamente en el umbral: se conserva
    s[0, 1] = [60, 60, 90, 90, 0.24, 0]
    _, conf, _ = decodificar(s, 0.25, 0.45)
    assert len(conf) == 1


def test_CPU_019_deshace_letterbox_y_recorta_bordes():
    p = preprocesar(Image.new("RGB", (800, 600)), 640)
    out = a_imagen_original([[0, 0, 700, 700]], p)
    assert out[0, 0] == 0 and out[0, 1] == 0
    assert out[0, 2] == 800 and out[0, 3] == 600


def test_CPU_020_posprocesar_limita_max_detecciones_y_ordena():
    s = np.zeros((1, 300, 6), dtype=np.float32)
    for i in range(30):
        s[0, i] = [i * 20, 100, i * 20 + 10, 110, 0.3 + i * 0.01, 0]
    p = preprocesar(Image.new("RGB", (640, 640)), 640)
    cajas = posprocesar(s, p, 0.25, 0.45, 20)
    assert len(cajas) == 20
    assert all(cajas[i].confianza >= cajas[i + 1].confianza for i in range(19))


# ---------------- Explicabilidad (ia/explicabilidad.py) ----------------
def test_CPU_021_superponer_roi_genera_data_url_jpeg():
    url = superponer_roi(Image.new("RGB", (400, 300)), [Caja(10, 10, 100, 100, 0.9, 0)])
    assert url.startswith("data:image/jpeg;base64,")


def test_CPU_022_superponer_roi_reduce_imagenes_grandes():
    import base64
    url = superponer_roi(Image.new("RGB", (3000, 2000)), [])
    im = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
    assert max(im.size) == 960


# ---------------- Servicio de inferencia (api/servicio_inferencia.py) ----------------
def test_CPU_023_analizar_sin_detecciones():
    r = analizar(Image.new("RGB", (800, 600)), ModeloFalso(), CFG)
    assert r.clasificacion == "sin_hallazgos" and r.imagen_resultado is None and r.confianza == 0


def test_CPU_024_analizar_roi_normalizada_y_contrato():
    r = analizar(Image.new("RGB", (800, 600)), ModeloFalso([[200, 200, 400, 400, 0.91, 0]]), CFG)
    roi = r.rois[0]
    assert all(0 <= v <= 1 for v in (roi.x, roi.y, roi.ancho, roi.alto, roi.confianza))
    assert r.modelo_version == CFG.version_modelo and "No constituye un diagnóstico" in r.aviso
    assert r.metricas.latencia_ms >= r.metricas.inferencia_ms


def test_CPU_025_analizar_no_escribe_en_disco(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    antes_tmp = set(os.listdir(tempfile.gettempdir()))
    analizar(Image.new("RGB", (800, 600)), ModeloFalso([[200, 200, 400, 400, 0.91, 0]]), CFG)
    assert list(tmp_path.iterdir()) == []
    assert set(os.listdir(tempfile.gettempdir())) - antes_tmp == set()


# ---------------- Admisión y errores (api/admision.py, api/errores.py) ----------------
def test_CPU_034_admision_modelo_no_listo_503():
    e = _codigo(lambda: Admision(2).entrar(False))
    assert e.estado == 503 and e.codigo == "MODELO_NO_LISTO"


def test_CPU_036_error_interno_sin_trazas_tecnicas():
    r = asyncio.run(manejar_error_interno(None, RuntimeError("Traceback secreto /ruta/x.py")))
    cuerpo = json.loads(r.body)
    assert r.status_code == 500 and cuerpo["error"]["codigo"] == "ERROR_INTERNO"
    assert "Traceback" not in r.body.decode() and "x.py" not in r.body.decode()


# ---------------- Endpoints (api/main.py) ----------------
@pytest.fixture
def cliente():
    with TestClient(crear_app(Config(), ModeloFalso([[200, 200, 400, 400, 0.91, 0]]))) as c:
        yield c


def test_CPU_039_cors_solo_admite_el_origen_configurado(cliente):
    ok = cliente.options("/api/v1/inferencias", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    malo = cliente.options("/api/v1/inferencias", headers={
        "Origin": "http://sitio-ajeno.com", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in malo.headers


# ---------------- Base de datos y configuración ----------------
def test_CPU_040_normaliza_url_postgres_a_psycopg():
    assert db._normalizar("postgres://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
    assert db._normalizar("postgresql://u:p@h/d") == "postgresql+psycopg://u:p@h/d"


def test_CPU_041_acota_confianza_entre_0_y_1():
    assert db._acotar(1.7) == 1.0 and db._acotar(-0.2) == 0.0 and db._acotar(0.5) == 0.5


def test_CPU_042_sin_database_url_estado_no_configurada(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db.reiniciar()
    assert db.estado() == "no_configurada"
    db.reiniciar()


def test_CPU_043_config_umbrales_por_defecto_iguales_al_entrenamiento():
    c = Config()
    assert (c.tamano_img, c.umbral_conf, c.umbral_iou) == (640, 0.25, 0.45)
    assert c.formatos_ok == ("JPEG", "PNG")


def test_CPU_044_sha256_del_modelo(tmp_path):
    f = tmp_path / "m.onnx"
    f.write_bytes(b"abc")
    assert sha256_archivo(str(f)) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
