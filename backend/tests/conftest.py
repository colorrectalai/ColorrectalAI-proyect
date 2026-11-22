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


def salida_seg_falsa(cx=300, cy=300, lado=200):
    """Salida de un YOLO-seg clásico con UNA detección cuadrada y su máscara (lienzo 640x640)."""
    det = np.zeros((1, 37, 8400), dtype=np.float32)
    det[0, :4, 0] = [cx, cy, lado, lado]
    det[0, 4, 0] = 0.9                 # confianza de la única clase
    det[0, 5, 0] = 1.0                 # el coeficiente 0 activa el prototipo 0
    protos = np.full((32, 160, 160), -12, dtype=np.float32)
    a, b = int((cx - lado / 2) / 4), int((cx + lado / 2) / 4)
    c, d = int((cy - lado / 2) / 4), int((cy + lado / 2) / 4)
    protos[0, c:d, a:b] = 12
    return det, protos


class ModeloFalsoSeg(ModeloFalso):
    """Imita a un modelo de segmentación: detecciones + prototipos de máscara."""
    es_segmentacion = True

    def ejecutar_seg(self, tensor):
        if not self.con_deteccion:
            return np.zeros((1, 37, 8400), dtype=np.float32), np.zeros((32, 160, 160), dtype=np.float32)
        return salida_seg_falsa()


@pytest.fixture
def cliente_seg():
    with TestClient(crear_app(Config(), ModeloFalsoSeg())) as c:
        yield c
