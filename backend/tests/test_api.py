import asyncio

import pytest
from fastapi.testclient import TestClient

from api.admision import Admision
from api.errores import ErrorAPI
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


# --- DEF-02: límite de 10 MB ---
def test_limite_por_defecto_es_10_mb():
    assert Config().max_bytes_imagen == 10 * 1024 * 1024


def test_archivo_mayor_a_10_mb_da_413(cliente):
    r = _post(cliente, b"0" * (10 * 1024 * 1024 + 1))
    assert r.status_code == 413
    j = r.json()["error"]
    assert j["codigo"] == "ARCHIVO_GRANDE" and "10 MB" in j["mensaje"]


# --- DEF-03 / DEF-10: errores del framework en JSON y en español ---
def test_422_sin_archivo_usa_formato_de_error(cliente):
    r = cliente.post("/api/v1/inferencias")
    assert r.status_code == 422
    assert r.json()["error"]["codigo"] == "SOLICITUD_INVALIDA"
    assert "detail" not in r.json()


def test_404_usa_formato_de_error(cliente):
    r = cliente.get("/api/v1/no-existe")
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == "RUTA_NO_ENCONTRADA"


def test_405_usa_formato_de_error(cliente):
    r = cliente.get("/api/v1/inferencias")
    assert r.status_code == 405
    assert r.json()["error"]["codigo"] == "METODO_NO_PERMITIDO"


def test_salud_informa_base_de_datos(cliente):
    assert cliente.get("/api/v1/salud").json()["base_datos"] == "no_configurada"


# --- DEF-09: se espera cupo en vez de rechazar al instante ---
def test_admision_espera_su_turno():
    async def probar():
        a = Admision(1, espera_max_s=2)
        orden = []

        async def uno():
            async with a.cupo():
                await asyncio.sleep(0.1)
                orden.append(1)

        async def dos():
            await asyncio.sleep(0.01)
            async with a.cupo():
                orden.append(2)

        await asyncio.gather(uno(), dos())
        assert orden == [1, 2]
    asyncio.run(probar())


def test_admision_rechaza_si_se_agota_la_espera():
    async def probar():
        a = Admision(1, espera_max_s=0.1)
        async with a.cupo():
            with pytest.raises(ErrorAPI) as e:
                async with a.cupo():
                    pass
            assert e.value.codigo == "SIN_CUPO" and e.value.estado == 503
        async with a.cupo():        # el cupo se liberó
            pass
    asyncio.run(probar())
