"""Control de admisión: modelo listo y cupo disponible.

Si todos los cupos están ocupados la solicitud ESPERA hasta `espera_max_s` segundos;
solo si se agota la espera responde 503 SIN_CUPO.
"""
import asyncio
from contextlib import asynccontextmanager

from .errores import ErrorAPI


class Admision:
    def __init__(self, max_concurrentes: int, espera_max_s: float = 20.0):
        self._cupo = asyncio.Semaphore(max_concurrentes)
        self._espera = espera_max_s

    def entrar(self, modelo_listo: bool) -> None:
        if not modelo_listo:
            raise ErrorAPI(503, "MODELO_NO_LISTO",
                           "El modelo aún se está cargando. Intente de nuevo en unos segundos.")

    @asynccontextmanager
    async def cupo(self):
        """Uso: 'async with admision.cupo():'. Libera el cupo al salir, aunque haya error."""
        try:
            await asyncio.wait_for(self._cupo.acquire(), self._espera)
        except asyncio.TimeoutError:
            raise ErrorAPI(503, "SIN_CUPO", "El servicio está ocupado. Intente de nuevo en un momento.")
        try:
            yield
        finally:
            self._cupo.release()
