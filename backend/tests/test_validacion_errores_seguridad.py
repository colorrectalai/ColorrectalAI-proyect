"""Validación de archivos, admisión, manejo de errores, seguridad de tokens y configuración.

Cada prueba verifica un riesgo concreto: formatos y límites (RNF-015.2), concurrencia y modelo no listo
(RNF-013.2, RNF-017.1), errores sin fugas de información, tokens alterados (DEF-11) y variables de entorno.
"""
import asyncio
import io

import pytest
from PIL import Image

from api import seguridad
from api.admision import Admision
from api.errores import ErrorAPI
from api.validacion import validar_imagen
from ia.config import Config


def imagen(fmt="PNG", ancho=64, alto=48, modo="RGB"):
    buf = io.BytesIO()
    Image.new(modo, (ancho, alto), 128).save(buf, format=fmt)
    return buf.getvalue()


# ---------------- Validación de archivos ----------------
@pytest.mark.parametrize("fmt", ["PNG", "JPEG"])
def test_formatos_admitidos(fmt):
    assert validar_imagen(imagen(fmt), Config()).format == fmt


@pytest.mark.parametrize("fmt", ["BMP", "GIF", "TIFF", "WEBP", "ICO"])
def test_formatos_no_admitidos_dan_415(fmt):
    with pytest.raises(ErrorAPI) as e:
        validar_imagen(imagen(fmt, 64, 64), Config())
    assert (e.value.estado, e.value.codigo) == (415, "FORMATO_NO_ADMITIDO")


@pytest.mark.parametrize("modo", ["L", "RGBA", "P", "LA"])
def test_png_en_otros_modos_de_color_se_acepta(modo):
    assert validar_imagen(imagen("PNG", 64, 64, modo), Config()).size == (64, 64)


@pytest.mark.parametrize("datos", [b"%PDF-1.4 falso", b"<script>alert(1)</script>", b"\x89PNG\r\n\x1a\n roto",
                                   b"\xff\xd8\xff corrupto", b"MZ\x90\x00ejecutable"], ids=["pdf", "script", "png_roto",
                                                                                       "jpeg_roto", "exe"])
def test_contenido_que_no_es_imagen_da_415(datos):
    with pytest.raises(ErrorAPI) as e:
        validar_imagen(datos, Config())
    assert (e.value.estado, e.value.codigo) == (415, "ARCHIVO_INVALIDO")


def test_archivo_vacio_da_400():
    with pytest.raises(ErrorAPI) as e:
        validar_imagen(b"", Config())
    assert (e.value.estado, e.value.codigo) == (400, "ARCHIVO_VACIO")


def test_limite_de_tamano_exacto_y_un_byte_mas():
    cfg = Config(max_bytes_imagen=len(imagen()))
    assert validar_imagen(imagen(), cfg)
    with pytest.raises(ErrorAPI) as e:
        validar_imagen(imagen() + b"x", Config(max_bytes_imagen=len(imagen())))
    assert (e.value.estado, e.value.codigo) == (413, "ARCHIVO_GRANDE")


@pytest.mark.parametrize("lado,ok", [(32, True), (31, False)])
def test_lado_minimo_32_px(lado, ok):
    if ok:
        assert validar_imagen(imagen("PNG", lado, lado), Config())
    else:
        with pytest.raises(ErrorAPI) as e:
            validar_imagen(imagen("PNG", lado, lado), Config())
        assert e.value.codigo == "IMAGEN_DEMASIADO_PEQUENA"


@pytest.mark.parametrize("lado,ok", [(200, True), (201, False)])
def test_lado_maximo_configurable(lado, ok):
    cfg = Config(max_lado_px=200)
    if ok:
        assert validar_imagen(imagen("PNG", lado, 40), cfg)
    else:
        with pytest.raises(ErrorAPI) as e:
            validar_imagen(imagen("PNG", lado, 40), cfg)
        assert (e.value.estado, e.value.codigo) == (422, "IMAGEN_DEMASIADO_GRANDE")


def test_bomba_de_descompresion_se_rechaza_sin_caer():
    buf = io.BytesIO()
    Image.new("1", (12000, 12000)).save(buf, format="PNG")      # 144 MP en pocos KB
    with pytest.raises(ErrorAPI) as e:
        validar_imagen(buf.getvalue(), Config(max_lado_px=20000))
    assert e.value.estado in (415, 422)


# ---------------- Admisión ----------------
def test_modelo_no_listo_da_503():
    with pytest.raises(ErrorAPI) as e:
        Admision(1).entrar(False)
    assert (e.value.estado, e.value.codigo) == (503, "MODELO_NO_LISTO")


def test_modelo_listo_no_lanza():
    Admision(1).entrar(True)


def test_cupo_se_libera_aunque_haya_error():
    async def flujo():
        a = Admision(1, espera_max_s=0.2)
        with pytest.raises(RuntimeError):
            async with a.cupo():
                raise RuntimeError("falla dentro")
        async with a.cupo():          # si no se liberó, aquí daría SIN_CUPO
            return True
    assert asyncio.run(flujo())


def test_respeta_el_maximo_de_concurrentes():
    async def flujo():
        a, activos, maximo = Admision(2, espera_max_s=5), 0, 0

        async def tarea():
            nonlocal activos, maximo
            async with a.cupo():
                activos += 1; maximo = max(maximo, activos)
                await asyncio.sleep(0.02)
                activos -= 1
        await asyncio.gather(*(tarea() for _ in range(6)))
        return maximo
    assert asyncio.run(flujo()) == 2


# ---------------- Errores de la API ----------------
@pytest.mark.parametrize("metodo,ruta,estado,codigo", [
    ("get", "/no-existe", 404, "RUTA_NO_ENCONTRADA"),
    ("get", "/api/v1/inferencias", 405, "METODO_NO_PERMITIDO"),
    ("post", "/api/v1/salud", 405, "METODO_NO_PERMITIDO"),
    ("get", "/api/v1/sesiones", 405, "METODO_NO_PERMITIDO"),
    ("delete", "/api/v1/usuarios", 405, "METODO_NO_PERMITIDO"),
    ("post", "/api/v1/inferencias", 422, "SOLICITUD_INVALIDA"),
])
def test_errores_en_formato_y_espanol(cliente, metodo, ruta, estado, codigo):
    r = getattr(cliente, metodo)(ruta)
    assert r.status_code == estado
    assert r.json()["error"]["codigo"] == codigo and r.json()["error"]["mensaje"]


def test_error_interno_no_filtra_detalles():
    from fastapi.testclient import TestClient
    from api.main import crear_app
    from tests.conftest import ModeloFalso, png_bytes

    class ModeloQueFalla(ModeloFalso):
        def ejecutar(self, tensor):
            raise RuntimeError("/ruta/secreta.py SELECT * FROM usuario")
    with TestClient(crear_app(Config(), ModeloQueFalla()), raise_server_exceptions=False) as c:
        r = c.post("/api/v1/inferencias", files={"imagen": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 500 and r.json()["error"]["codigo"] == "ERROR_INTERNO"
    assert "secreta" not in r.text and "SELECT" not in r.text and "Traceback" not in r.text


def test_cors_solo_para_el_origen_configurado(cliente):
    ok = cliente.options("/api/v1/salud", headers={"Origin": "http://localhost:5173",
                                                    "Access-Control-Request-Method": "GET"})
    malo = cliente.options("/api/v1/salud", headers={"Origin": "https://atacante.example",
                                                      "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert malo.headers.get("access-control-allow-origin") is None


# ---------------- Tokens de sesión ----------------
@pytest.mark.parametrize("token", ["", "sin-punto", ".", "a.b.c", "!!!.???", "eyJzdWIiOjF9.firma-falsa"])
def test_tokens_malformados_no_se_aceptan(token):
    assert seguridad.leer_token(token) is None


def test_token_con_carga_cambiada_no_se_acepta():
    token, _ = seguridad.crear_token(1)
    otro, _ = seguridad.crear_token(2)
    falso = otro.split(".")[0] + "." + token.split(".")[1]       # carga del usuario 2, firma del 1
    assert seguridad.leer_token(falso) is None


def test_token_vence_en_el_limite_exacto():
    token, vigencia = seguridad.crear_token(5, ahora=100)
    assert seguridad.leer_token(token, ahora=100 + vigencia) == 5
    assert seguridad.leer_token(token, ahora=100 + vigencia + 1) is None


@pytest.mark.parametrize("clave", ["ñandú-Ñ123", "contraseña con espacios", "😀😀😀😀😀😀😀😀", "a" * 128])
def test_hash_soporta_unicode_y_longitud_maxima(clave):
    assert seguridad.verificar_contrasena(clave, seguridad.hash_contrasena(clave))


@pytest.mark.parametrize("guardado", ["", "scrypt$", "md5$1$2$3$aa$bb", "scrypt$x$8$1$aa$bb", "texto-plano"])
def test_hash_corrupto_o_de_otro_algoritmo_no_verifica(guardado):
    assert seguridad.verificar_contrasena("x", guardado) is False


# ---------------- Configuración por variables de entorno ----------------
@pytest.mark.parametrize("var,valor,campo,esperado", [
    ("MAX_MB_IMAGEN", "5", "max_bytes_imagen", 5 * 1024 * 1024),
    ("MAX_CONCURRENTES", "1", "max_concurrentes", 1),
    ("UMBRAL_CONF", "0.4", "umbral_conf", 0.4),
    ("MODELO_VERSION", "seg-9", "version_modelo", "seg-9"),
    ("MODELO_SHA256", "ABC", "sha256_modelo", "abc"),
])
def test_config_lee_variables_de_entorno(monkeypatch, var, valor, campo, esperado):
    monkeypatch.setenv(var, valor)
    assert getattr(Config(), campo) == esperado


def test_cors_acepta_varios_origenes_separados_por_coma(monkeypatch):
    monkeypatch.setenv("CORS_ORIGENES", "https://a.app, https://b.app ,")
    assert Config().origenes_cors == ("https://a.app", "https://b.app")
