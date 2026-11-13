from fastapi.testclient import TestClient

from api.main import crear_app
from ia.config import Config
from .conftest import ModeloFalso, png_bytes


def _post(cliente, datos, nombre="a.png", tipo="image/png"):
    return cliente.post("/api/v1/inferencias", files={"imagen": (nombre, datos, tipo)})


def test_salud(cliente):
    r = cliente.get("/api/v1/salud")
    assert r.status_code == 200 and r.json()["modelo_listo"] is True


def test_inferencia_con_roi(cliente):
    r = _post(cliente, png_bytes())
    assert r.status_code == 200
    j = r.json()
    assert j["clasificacion"] == "posible_region"
    assert len(j["rois"]) == 1 and 0.9 < j["confianza"] < 0.92
    assert j["imagen_resultado"].startswith("data:image/jpeg;base64,")
    assert "diagnóstico" in j["aviso"]
    assert j["metricas"]["latencia_ms"] > 0


def test_roi_se_ubica_en_la_imagen_original(cliente):
    # 800x600 -> escala 0.8, relleno vertical 80 px. Caja del modelo (200,200)-(400,400)
    j = _post(cliente, png_bytes(800, 600)).json()
    roi = j["rois"][0]
    assert abs(roi["x"] - 0.3125) < 0.01          # (200-0)/0.8/800
    assert abs(roi["y"] - 0.25) < 0.01            # (200-80)/0.8/600
    assert 0 < roi["ancho"] < 1 and 0 < roi["alto"] < 1


def test_sin_hallazgos(cliente_sin_hallazgos):
    j = _post(cliente_sin_hallazgos, png_bytes()).json()
    assert j["clasificacion"] == "sin_hallazgos" and j["rois"] == [] and j["confianza"] == 0


def test_archivo_no_es_imagen(cliente):
    r = _post(cliente, b"esto no es una imagen", "a.png")
    assert r.status_code == 415
    assert r.json()["error"]["codigo"] == "ARCHIVO_INVALIDO"


def test_formato_no_admitido(cliente):
    r = _post(cliente, png_bytes(formato="BMP"), "a.bmp", "image/bmp")
    assert r.status_code == 415


def test_archivo_vacio(cliente):
    assert _post(cliente, b"").status_code == 400


def test_modelo_no_listo_da_503():
    modelo = ModeloFalso()
    modelo.listo = False
    with TestClient(crear_app(Config(), modelo)) as c:
        r = _post(c, png_bytes())
    assert r.status_code == 503 and r.json()["error"]["codigo"] == "MODELO_NO_LISTO"
