import numpy as np
from PIL import Image

from ia.explicabilidad import mascara_blanco_negro
from ia.posprocesamiento import decodificar, decodificar_seg, nms, posprocesar_seg
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


# --- Segmentación (máscaras) ---
def _salida_seg(lado=200):
    det = np.zeros((1, 37, 8400), dtype=np.float32)
    det[0, :4, 0] = [300, 300, lado, lado]
    det[0, 4, 0], det[0, 5, 0] = 0.9, 1.0
    protos = np.full((32, 160, 160), -12, dtype=np.float32)
    protos[0, 50:100, 50:100] = 12             # cuadrado de 200x200 px en el lienzo (x e y: 200-400)
    return det, protos


def test_mascara_seg_cae_en_la_posicion_correcta():
    prep = preprocesar(Image.new("RGB", (800, 600)), 640)      # escala 0.8, relleno arriba/abajo de 80 px
    det, protos = _salida_seg()
    cajas, mascara = posprocesar_seg(det, protos, prep, 0.25, 0.45, 20, 640)
    assert len(cajas) == 1 and mascara.shape == (600, 800)
    esperada = np.zeros((600, 800), dtype=bool)
    esperada[150:400, 250:500] = True                           # (200-80)/0.8 ... (400-80)/0.8
    iou = (mascara & esperada).sum() / (mascara | esperada).sum()
    assert iou > 0.95


def test_mascara_seg_sin_detecciones():
    prep = preprocesar(Image.new("RGB", (800, 600)), 640)
    det = np.zeros((1, 37, 8400), dtype=np.float32)
    cajas, mascara = posprocesar_seg(det, np.zeros((32, 160, 160), np.float32), prep, 0.25, 0.45, 20, 640)
    assert cajas == [] and mascara is None


def test_decodificar_seg_formato_end_to_end():
    salida = np.zeros((1, 300, 38), dtype=np.float32)
    salida[0, 0, :6] = [100, 100, 200, 200, 0.8, 0]
    salida[0, 0, 6] = 1.0
    xyxy, conf, cls, coefs = decodificar_seg(salida, 0.25, 0.45)
    assert len(conf) == 1 and coefs.shape == (1, 32) and conf[0] > 0.79


def test_mascara_blanco_negro_solo_tiene_0_y_255():
    import base64
    import io
    m = np.zeros((60, 80), dtype=bool)
    m[10:30, 20:50] = True
    url = mascara_blanco_negro(m)
    assert url.startswith("data:image/png;base64,")
    img = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
    a = np.asarray(img)
    assert img.mode == "L" and a.shape == (60, 80)
    assert set(np.unique(a)) == {0, 255} and (a == 255).sum() == m.sum()
