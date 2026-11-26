"""Contraseñas y sesiones de los usuarios de la interfaz (DEF-11). Solo biblioteca estándar.

- Contraseñas: scrypt (n=2^14, r=8, p=1) con sal aleatoria de 16 bytes. Nunca se guarda la contraseña.
- Sesiones: token firmado con HMAC-SHA256 (formato carga.firma, ambos en base64url) que caduca a las
  TOKEN_HORAS horas. La clave sale de TOKEN_SECRETO; si no está definida se genera una al arrancar
  (las sesiones se pierden al reiniciar, por eso en producción hay que definirla).
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time

log = logging.getLogger("colorrectalai.seguridad")

_N, _R, _P, _LARGO = 2 ** 14, 8, 1, 32
HORAS_SESION = float(os.getenv("TOKEN_HORAS", "8"))


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def _de_b64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def hash_contrasena(contrasena: str) -> str:
    sal = secrets.token_bytes(16)
    clave = hashlib.scrypt(contrasena.encode("utf-8"), salt=sal, n=_N, r=_R, p=_P, dklen=_LARGO)
    return f"scrypt${_N}${_R}${_P}${_b64(sal)}${_b64(clave)}"


def verificar_contrasena(contrasena: str, guardado: str) -> bool:
    try:
        algoritmo, n, r, p, sal, clave = guardado.split("$")
        if algoritmo != "scrypt":
            return False
        calculada = hashlib.scrypt(contrasena.encode("utf-8"), salt=_de_b64(sal), n=int(n), r=int(r),
                                   p=int(p), dklen=len(_de_b64(clave)))
        return hmac.compare_digest(calculada, _de_b64(clave))
    except (ValueError, TypeError):
        return False


# Hash de relleno: se verifica contra él cuando el correo no existe, para que la respuesta tarde
# lo mismo y no se pueda averiguar qué correos están registrados midiendo el tiempo.
HASH_RELLENO = hash_contrasena(secrets.token_urlsafe(16))

_secreto_env = os.getenv("TOKEN_SECRETO", "").strip()
if not _secreto_env:
    log.warning("TOKEN_SECRETO no está definido: se usa una clave temporal y las sesiones "
                "se perderán al reiniciar la API.")
_SECRETO = (_secreto_env or secrets.token_urlsafe(32)).encode("utf-8")


def crear_token(id_usuario: int, ahora: float | None = None) -> tuple[str, int]:
    """Devuelve (token, segundos de validez)."""
    vigencia = int(HORAS_SESION * 3600)
    carga = _b64(json.dumps({"sub": id_usuario, "exp": int((ahora or time.time()) + vigencia)},
                            separators=(",", ":")).encode("utf-8"))
    firma = _b64(hmac.new(_SECRETO, carga.encode("ascii"), hashlib.sha256).digest())
    return f"{carga}.{firma}", vigencia


def leer_token(token: str, ahora: float | None = None) -> int | None:
    """Devuelve el id del usuario si el token es auténtico y vigente; si no, None."""
    try:
        carga, firma = token.split(".")
        esperada = _b64(hmac.new(_SECRETO, carga.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(firma, esperada):
            return None
        datos = json.loads(_de_b64(carga))
        if int(datos["exp"]) < (ahora or time.time()):
            return None
        return int(datos["sub"])
    except (ValueError, KeyError, TypeError):
        return None
