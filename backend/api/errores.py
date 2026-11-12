"""Errores de la API: todo fallo termina en JSON con mensaje en español."""
from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorAPI(Exception):
    def __init__(self, estado: int, codigo: str, mensaje: str):
        self.estado, self.codigo, self.mensaje = estado, codigo, mensaje


def _json(estado, codigo, mensaje):
    return JSONResponse(status_code=estado, content={"error": {"codigo": codigo, "mensaje": mensaje}})


async def manejar_error_api(_: Request, exc: ErrorAPI):
    return _json(exc.estado, exc.codigo, exc.mensaje)


async def manejar_error_interno(_: Request, exc: Exception):
    return _json(500, "ERROR_INTERNO", "Ocurrió un error interno al procesar la imagen.")
