"""Errores de la API: todo fallo termina en JSON con mensaje en español."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorAPI(Exception):
    def __init__(self, estado: int, codigo: str, mensaje: str):
        self.estado, self.codigo, self.mensaje = estado, codigo, mensaje


def _json(estado, codigo, mensaje):
    return JSONResponse(status_code=estado, content={"error": {"codigo": codigo, "mensaje": mensaje}})


async def manejar_error_api(_: Request, exc: ErrorAPI):
    return _json(exc.estado, exc.codigo, exc.mensaje)


async def manejar_error_interno(_: Request, exc: Exception):
    return _json(500, "ERROR_INTERNO", "Ocurrió un error interno al procesar la imagen.")


async def manejar_validacion(request: Request, exc: RequestValidationError):
    """422 propio de FastAPI (falta el campo, tipo incorrecto...) en el formato y el idioma del proyecto."""
    if request.url.path.endswith("/inferencias"):
        return _json(422, "SOLICITUD_INVALIDA",
                     "La solicitud no es válida. Envíe una imagen en el campo 'imagen' (multipart/form-data).")
    campos = sorted({str(e["loc"][-1]) for e in exc.errors() if e.get("loc")})
    return _json(422, "SOLICITUD_INVALIDA",
                 "La solicitud no es válida. Revise los campos: " + ", ".join(campos) + "." if campos
                 else "La solicitud no es válida.")


_HTTP = {404: ("RUTA_NO_ENCONTRADA", "La ruta solicitada no existe."),
         405: ("METODO_NO_PERMITIDO", "Método no permitido para esta ruta.")}


async def manejar_http(_: Request, exc: StarletteHTTPException):
    """404/405 y demás errores HTTP generados por el framework."""
    codigo, mensaje = _HTTP.get(exc.status_code, ("ERROR_HTTP", "No se pudo procesar la solicitud."))
    return _json(exc.status_code, codigo, mensaje)
