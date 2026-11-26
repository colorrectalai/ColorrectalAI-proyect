"""Base de datos y usuarios (DEF-11).

Las pruebas de integración necesitan PostgreSQL y se saltan si no existe TEST_DATABASE_URL, por ejemplo:
    TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/colorrectalai_test pytest
Cada prueba de integración trabaja sobre la base vacía (se borra el esquema public antes).
"""
import os

import pytest
from fastapi.testclient import TestClient

from api import db, seguridad
from api.main import crear_app
from ia.config import Config
from tests.conftest import ModeloFalso, png_bytes

URL_PRUEBAS = os.getenv("TEST_DATABASE_URL", "").strip()
requiere_bd = pytest.mark.skipif(not URL_PRUEBAS, reason="sin TEST_DATABASE_URL (PostgreSQL de pruebas)")
SHA_FALSO = "a" * 64


class ModeloConSha(ModeloFalso):
    sha256_real = SHA_FALSO


# ---------------- Seguridad (sin base de datos) ----------------
def test_hash_no_guarda_la_contrasena_y_verifica():
    h = seguridad.hash_contrasena("ClaveSegura123")
    assert "ClaveSegura123" not in h and h.startswith("scrypt$")
    assert seguridad.verificar_contrasena("ClaveSegura123", h)
    assert not seguridad.verificar_contrasena("otra-clave", h)


def test_hash_usa_sal_distinta_cada_vez():
    assert seguridad.hash_contrasena("igual1234") != seguridad.hash_contrasena("igual1234")


def test_hash_corrupto_no_verifica():
    assert not seguridad.verificar_contrasena("x", "texto-que-no-es-un-hash")


def test_token_valido_alterado_y_vencido():
    token, vigencia = seguridad.crear_token(7, ahora=1_000)
    assert seguridad.leer_token(token, ahora=1_000) == 7
    assert seguridad.leer_token(token[:-2] + "xx", ahora=1_000) is None
    assert seguridad.leer_token(token, ahora=1_000 + vigencia + 1) is None
    assert seguridad.leer_token("basura", ahora=1_000) is None


def test_sin_base_el_registro_responde_503(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db.reiniciar()
    with TestClient(crear_app(Config(), ModeloFalso())) as c:
        r = c.post("/api/v1/usuarios", json={"nombre": "Ana", "correo": "ana@x.co",
                                              "contrasena": "12345678", "acepta_aviso": True})
    assert r.status_code == 503 and r.json()["error"]["codigo"] == "BASE_NO_DISPONIBLE"


def test_422_de_usuarios_no_habla_de_imagenes(cliente):
    r = cliente.post("/api/v1/sesiones", json={"correo": "a@b.co"})
    assert r.status_code == 422
    assert "imagen" not in r.json()["error"]["mensaje"] and "contrasena" in r.json()["error"]["mensaje"]


# ---------------- Integración con PostgreSQL ----------------
@pytest.fixture
def cliente_bd(monkeypatch):
    from sqlalchemy import create_engine, text
    limpio = create_engine(db._normalizar(URL_PRUEBAS))
    with limpio.begin() as c:
        c.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    limpio.dispose()
    monkeypatch.setenv("DATABASE_URL", URL_PRUEBAS)
    db.reiniciar()
    # La misma versión que usa el arranque: evita la carrera entre el registro en segundo plano
    # (lifespan) y el registro explícito de la prueba.
    with TestClient(crear_app(Config(version_modelo="prueba-0.1"), ModeloConSha())) as c:
        assert db.preparar(SHA_FALSO, "prueba-0.1")      # el arranque también lo llama; es idempotente
        yield c
    db.reiniciar()


def _consulta(sql):
    from sqlalchemy import text
    with db.obtener_engine().connect() as c:
        return c.execute(text(sql)).all()


@requiere_bd
def test_arranque_crea_esquema_datos_y_modelo_activo(cliente_bd):
    tablas = _consulta("SELECT count(*) FROM information_schema.tables "
                       "WHERE table_schema='public' AND table_type='BASE TABLE'")[0][0]
    assert tablas == 18
    assert _consulta("SELECT count(*) FROM catalogo_error")[0][0] == 13
    activos = _consulta("SELECT version, sha256_pesos FROM version_modelo WHERE estado='activo'")
    assert activos == [("prueba-0.1", SHA_FALSO)]
    assert _consulta("SELECT count(*) FROM v_metricas_modelo WHERE version='baseline-0.1'")[0][0] == 12
    assert cliente_bd.get("/api/v1/salud").json()["base_datos"] == "conectada"


@requiere_bd
def test_preparar_dos_veces_no_duplica(cliente_bd):
    assert db.preparar(SHA_FALSO, "prueba-0.1")
    assert _consulta("SELECT count(*) FROM investigador")[0][0] == 1
    assert _consulta("SELECT count(*) FROM version_modelo")[0][0] == 2


@requiere_bd
def test_nuevo_modelo_retira_el_anterior(cliente_bd):
    assert db.preparar("b" * 64, "prueba-0.2")
    assert _consulta("SELECT version FROM version_modelo WHERE estado='activo'") == [("prueba-0.2",)]


@requiere_bd
def test_inferencia_queda_registrada_sin_imagen(cliente_bd):
    r = cliente_bd.post("/api/v1/inferencias", files={"imagen": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 200
    cliente_bd.post("/api/v1/inferencias", files={"imagen": ("v.png", b"", "image/png")})
    filas = _consulta("SELECT formato_archivo, num_roi, id_error IS NULL FROM solicitud_inferencia "
                      "ORDER BY id_solicitud")
    assert filas == [("png", 1, True), (None, 0, False)]
    assert _consulta("SELECT count(*) FROM resultado_roi")[0][0] == 1


@requiere_bd
def test_registro_inicio_y_sesion(cliente_bd):
    nuevo = {"nombre": "  Ana   María ", "correo": "Ana@Ejemplo.CO", "contrasena": "ClaveSegura123",
             "acepta_aviso": True}
    r = cliente_bd.post("/api/v1/usuarios", json=nuevo)
    assert r.status_code == 201
    assert r.json()["usuario"] == {"id": r.json()["usuario"]["id"], "nombre": "Ana María",
                                   "correo": "ana@ejemplo.co"}
    guardado = _consulta("SELECT hash_contrasena FROM usuario")[0][0]
    assert "ClaveSegura123" not in guardado and guardado.startswith("scrypt$")

    assert cliente_bd.post("/api/v1/usuarios", json=nuevo).json()["error"]["codigo"] == "CORREO_REGISTRADO"

    mala = cliente_bd.post("/api/v1/sesiones", json={"correo": "ana@ejemplo.co", "contrasena": "incorrecta"})
    assert mala.status_code == 401 and mala.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"
    nadie = cliente_bd.post("/api/v1/sesiones", json={"correo": "nadie@x.co", "contrasena": "ClaveSegura123"})
    assert nadie.status_code == 401

    ok = cliente_bd.post("/api/v1/sesiones", json={"correo": "ANA@ejemplo.co", "contrasena": "ClaveSegura123"})
    assert ok.status_code == 200
    yo = cliente_bd.get("/api/v1/usuarios/yo", headers={"Authorization": "Bearer " + ok.json()["token"]})
    assert yo.status_code == 200 and yo.json()["correo"] == "ana@ejemplo.co"
    assert cliente_bd.get("/api/v1/usuarios/yo").status_code == 401


@requiere_bd
@pytest.mark.parametrize("cambio,parte", [
    ({"correo": "sin-arroba"}, "correo"), ({"contrasena": "corta"}, "8"),
    ({"nombre": "A"}, "nombre"), ({"acepta_aviso": False}, "aviso"),
])
def test_registro_valida_los_datos(cliente_bd, cambio, parte):
    datos = {"nombre": "Ana", "correo": "ana@x.co", "contrasena": "ClaveSegura123", "acepta_aviso": True}
    r = cliente_bd.post("/api/v1/usuarios", json={**datos, **cambio})
    assert r.status_code == 422 and parte in r.json()["error"]["mensaje"]
