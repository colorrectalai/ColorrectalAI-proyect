"""Control de admisión: modelo listo y cupo disponible; si no, error 503."""
import asyncio

from .errores import ErrorAPI


class Admision:
    def __init__(self, max_concurrentes: int):
        self._cupo = asyncio.Semaphore(max_concurrentes)

    def entrar(self, modelo_listo: bool):
        if not modelo_listo:
            raise ErrorAPI(503, "MODELO_NO_LISTO",
                           "El modelo aún se está cargando. Intente de nuevo en unos segundos.")
        if self._cupo.locked():
            raise ErrorAPI(503, "SIN_CUPO", "El servicio está ocupado. Intente de nuevo en un momento.")
        return self._cupo       # se usa con 'async with'
