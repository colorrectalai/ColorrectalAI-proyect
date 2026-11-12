import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import crear_app
from ia.config import Config


class ModeloFalso:
    """Imita al adaptador ONNX: devuelve una sola detección en formato end-to-end (1, N, 6)."""
    listo = True
    tamano_entrada = 640
    sha256_real = "falso"

    def __init__(self, con_deteccion=True):
        self.con_deteccion = con_deteccion

    def cargar(self):
        pass

    def ejecutar(self, tensor):
        salida = np.zeros((1, 300, 6), dtype=np.float32)
        if self.con_deteccion:
            salida[0, 0] = [200, 200, 400, 400, 0.91, 0]
        return salida


def png_bytes(ancho=800, alto=600, formato="PNG"):
    buf = io.BytesIO()
    Image.new("RGB", (ancho, alto), (180, 80, 80)).save(buf, format=formato)
    return buf.getvalue()


@pytest.fixture
def cliente():
    with TestClient(crear_app(Config(), ModeloFalso())) as c:
        yield c


@pytest.fixture
def cliente_sin_hallazgos():
    with TestClient(crear_app(Config(), ModeloFalso(con_deteccion=False))) as c:
        yield c
