"""Registro e inicio de sesión de los usuarios de la interfaz web (DEF-11).

POST /api/v1/usuarios     crea la cuenta y devuelve una sesión          (201)
POST /api/v1/sesiones     inicia sesión con correo y contraseña         (200)
GET  /api/v1/usuarios/yo  datos del usuario de la sesión (Bearer token) (200)

Requiere base de datos: sin DATABASE_URL responde 503 BASE_NO_DISPONIBLE.
"""
import re

from fastapi import APIRouter, Header
from starlette.concurrency import run_in_threadpool

from . import db
from .errores import ErrorAPI
from .esquemas import NuevoUsuario, Sesion, SolicitudSesion, Usuario
from .seguridad import HASH_RELLENO, crear_token, hash_contrasena, leer_token, verificar_contrasena

router = APIRouter(prefix="/api/v1", tags=["usuarios"])

_CORREO = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")
_SQL_USUARIO = "SELECT id_usuario, nombre_completo, correo, hash_contrasena, activo FROM usuario "


def _engine():
    engine = db.obtener_engine()
    if engine is None:
        raise ErrorAPI(503, "BASE_NO_DISPONIBLE",
                       "El registro de usuarios no está disponible: la base de datos no está configurada.")
    return engine


def _datos_invalidos(mensaje: str):
    return ErrorAPI(422, "DATOS_INVALIDOS", mensaje)


def _normalizar_correo(correo: str) -> str:
    return correo.strip().lower()


def _sesion(fila) -> Sesion:
    token, vigencia = crear_token(fila.id_usuario)
    return Sesion(token=token, expira_en_s=vigencia,
                  usuario=Usuario(id=fila.id_usuario, nombre=fila.nombre_completo, correo=fila.correo))


def _registrar(datos: NuevoUsuario) -> Sesion:
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError, OperationalError
    nombre, correo = " ".join(datos.nombre.split()), _normalizar_correo(datos.correo)
    if not 2 <= len(nombre) <= 120:
        raise _datos_invalidos("Escriba su nombre completo (entre 2 y 120 caracteres).")
    if len(correo) > 120 or not _CORREO.match(correo):
        raise _datos_invalidos("Escriba un correo electrónico válido.")
    if not 8 <= len(datos.contrasena) <= 128:
        raise _datos_invalidos("La contraseña debe tener entre 8 y 128 caracteres.")
    if not datos.acepta_aviso:
        raise _datos_invalidos("Debe aceptar el aviso legal para crear la cuenta.")
    clave = hash_contrasena(datos.contrasena)
    try:
        with _engine().begin() as c:
            fila = c.execute(text(
                "INSERT INTO usuario (correo, nombre_completo, hash_contrasena, acepto_aviso_en, ultimo_acceso) "
                "VALUES (:correo, :nombre, :clave, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) "
                "RETURNING id_usuario, nombre_completo, correo"),
                {"correo": correo, "nombre": nombre, "clave": clave}).one()
    except IntegrityError:
        raise ErrorAPI(409, "CORREO_REGISTRADO", "Ya existe una cuenta con ese correo. Inicie sesión.")
    except OperationalError:
        raise ErrorAPI(503, "BASE_NO_DISPONIBLE", "No se pudo conectar con la base de datos. Intente más tarde.")
    return _sesion(fila)


def _iniciar(datos: SolicitudSesion) -> Sesion:
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError
    try:
        with _engine().begin() as c:
            fila = c.execute(text(_SQL_USUARIO + "WHERE correo = :correo"),
                             {"correo": _normalizar_correo(datos.correo)}).first()
            ok = verificar_contrasena(datos.contrasena, fila.hash_contrasena if fila else HASH_RELLENO)
            if not (fila and ok and fila.activo):
                raise ErrorAPI(401, "CREDENCIALES_INVALIDAS", "Correo o contraseña incorrectos.")
            c.execute(text("UPDATE usuario SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id_usuario = :id"),
                      {"id": fila.id_usuario})
    except OperationalError:
        raise ErrorAPI(503, "BASE_NO_DISPONIBLE", "No se pudo conectar con la base de datos. Intente más tarde.")
    return _sesion(fila)


def _yo(autorizacion: str | None) -> Usuario:
    from sqlalchemy import text
    token = (autorizacion or "").removeprefix("Bearer ").strip()
    id_usuario = leer_token(token) if token else None
    if id_usuario is None:
        raise ErrorAPI(401, "SESION_INVALIDA", "La sesión no es válida o ya expiró. Inicie sesión de nuevo.")
    with _engine().connect() as c:
        fila = c.execute(text(_SQL_USUARIO + "WHERE id_usuario = :id"), {"id": id_usuario}).first()
    if not fila or not fila.activo:
        raise ErrorAPI(401, "SESION_INVALIDA", "La sesión no es válida o ya expiró. Inicie sesión de nuevo.")
    return Usuario(id=fila.id_usuario, nombre=fila.nombre_completo, correo=fila.correo)


@router.post("/usuarios", response_model=Sesion, status_code=201)
async def registrar_usuario(datos: NuevoUsuario):
    return await run_in_threadpool(_registrar, datos)


@router.post("/sesiones", response_model=Sesion)
async def iniciar_sesion(datos: SolicitudSesion):
    return await run_in_threadpool(_iniciar, datos)


@router.get("/usuarios/yo", response_model=Usuario)
async def usuario_actual(authorization: str | None = Header(None)):
    return await run_in_threadpool(_yo, authorization)
