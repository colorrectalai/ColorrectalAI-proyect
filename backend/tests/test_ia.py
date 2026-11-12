import numpy as np
from PIL import Image

from ia.posprocesamiento import decodificar, nms
from ia.preprocesamiento import preprocesar


def test_letterbox_conserva_proporcion():
    p = preprocesar(Image.new("RGB", (800, 600)), 640)
    assert p.tensor.shape == (1, 3, 640, 640) and p.tensor.dtype == np.float32
    assert p.escala == 0.8 and p.pad_y == 80 and p.pad_x == 0


def test_formato_clasico_aplica_nms():
    # (1, 5, anclas): dos cajas casi iguales + una lejana
    s = np.zeros((1, 5, 100), dtype=np.float32)   # 100 anclas (el real trae 8400)
    s[0, :, 0] = [100, 100, 50, 50, 0.9]
    s[0, :, 1] = [102, 101, 50, 50, 0.8]
    s[0, :, 2] = [400, 400, 40, 40, 0.7]
    xyxy, conf, _ = decodificar(s, 0.25, 0.45)
    assert len(conf) == 2 and abs(conf[0] - 0.9) < 1e-6


def test_umbral_descarta_baja_confianza():
    s = np.zeros((1, 300, 6), dtype=np.float32)
    s[0, 0] = [10, 10, 50, 50, 0.1, 0]
    assert len(decodificar(s, 0.25, 0.45)[1]) == 0
