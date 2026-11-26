"""Filtro 3: posprocesamiento.

Convierte la salida cruda del ONNX en cajas sobre la imagen ORIGINAL.
Soporta los dos formatos que produce Ultralytics:
  A) end-to-end (YOLO26, NMS integrado):  (1, N, 6) -> x1, y1, x2, y2, conf, clase
  B) clásico (YOLOv8 / YOLO11):           (1, 4+nc, anclas) -> cx, cy, w, h, conf_clase...
Si tu .onnx muestra otra forma en `inspeccionar_onnx` del Colab, solo hay que tocar aquí.
"""
from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class Caja:
    x1: float
    y1: float
    x2: float
    y2: float
    confianza: float
    clase: int


def _iou(a, b):
    x1 = np.maximum(a[0], b[:, 0]); y1 = np.maximum(a[1], b[:, 1])
    x2 = np.minimum(a[2], b[:, 2]); y2 = np.minimum(a[3], b[:, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (area_a + area_b - inter + 1e-9)


def nms(cajas, scores, umbral_iou):
    orden = scores.argsort()[::-1]
    mantener = []
    while orden.size:
        i = orden[0]
        mantener.append(int(i))
        resto = orden[1:]
        if resto.size == 0:
            break
        orden = resto[_iou(cajas[i], cajas[resto]) < umbral_iou]
    return mantener


def decodificar(salida, umbral_conf, umbral_iou):
    """Devuelve (xyxy, conf, clase) en coordenadas del lienzo del modelo (ej. 640x640)."""
    s = salida[0] if salida.ndim == 3 else salida

    if s.shape[-1] == 6 and s.shape[0] != 6:            # Formato A
        xyxy, conf, cls = s[:, :4], s[:, 4], s[:, 5].astype(int)
        ok = conf >= umbral_conf
        return xyxy[ok], conf[ok], cls[ok]

    if s.shape[0] < s.shape[1]:                          # Formato B: transponer
        s = s.T
    cxcywh, puntajes = s[:, :4], s[:, 4:]
    cls, conf = puntajes.argmax(axis=1), puntajes.max(axis=1)
    ok = conf >= umbral_conf
    cxcywh, conf, cls = cxcywh[ok], conf[ok], cls[ok]
    xyxy = np.stack([cxcywh[:, 0] - cxcywh[:, 2] / 2, cxcywh[:, 1] - cxcywh[:, 3] / 2,
                     cxcywh[:, 0] + cxcywh[:, 2] / 2, cxcywh[:, 1] + cxcywh[:, 3] / 2], axis=1)
    if len(conf):
        m = nms(xyxy, conf, umbral_iou)
        xyxy, conf, cls = xyxy[m], conf[m], cls[m]
    return xyxy, conf, cls


def a_imagen_original(xyxy, prep):
    """Deshace el letterbox y recorta a los bordes de la imagen original."""
    out = np.asarray(xyxy, dtype=np.float32).reshape(-1, 4).copy()
    if len(out) == 0:
        return out
    out[:, [0, 2]] = ((out[:, [0, 2]] - prep.pad_x) / prep.escala).clip(0, prep.ancho)
    out[:, [1, 3]] = ((out[:, [1, 3]] - prep.pad_y) / prep.escala).clip(0, prep.alto)
    return out


def posprocesar(salida, prep, umbral_conf, umbral_iou, max_det):
    xyxy, conf, cls = decodificar(salida, umbral_conf, umbral_iou)
    xyxy = a_imagen_original(xyxy, prep)
    orden = np.argsort(conf)[::-1][:max_det]
    return [Caja(*map(float, xyxy[i]), float(conf[i]), int(cls[i])) for i in orden]


# ---------------------------------------------------------------------------
# Segmentación (YOLO-seg): además de la caja, el modelo entrega una máscara por detección.
#   salida 0: (1, 4+nc+32, anclas)  -> caja, puntaje(s) de clase y 32 coeficientes de máscara
#   salida 1: (1, 32, 160, 160)     -> 32 "prototipos"; máscara = sigmoide(coeficientes @ prototipos)
# ---------------------------------------------------------------------------
N_COEF = 32


def decodificar_seg(salida, umbral_conf, umbral_iou, n_coef=N_COEF):
    """Devuelve (xyxy, conf, clase, coeficientes) en el lienzo del modelo.

    Acepta el formato clásico (NMS aquí) y el end-to-end (1, N, 6+32), igual que `decodificar`.
    """
    s = salida[0] if salida.ndim == 3 else salida

    if s.shape[-1] == 6 + n_coef and s.shape[0] > s.shape[-1]:     # end-to-end
        xyxy, conf, cls, coefs = s[:, :4], s[:, 4], s[:, 5].astype(int), s[:, 6:]
        ok = conf >= umbral_conf
        return xyxy[ok], conf[ok], cls[ok], coefs[ok]

    if s.shape[0] < s.shape[1]:                                      # clásico: transponer
        s = s.T
    nc = s.shape[1] - 4 - n_coef
    if nc < 1:
        raise ValueError(f"Salida de segmentación inesperada: {salida.shape}")
    cxcywh, puntajes, coefs = s[:, :4], s[:, 4:4 + nc], s[:, 4 + nc:]
    cls, conf = puntajes.argmax(axis=1), puntajes.max(axis=1)
    ok = conf >= umbral_conf
    cxcywh, conf, cls, coefs = cxcywh[ok], conf[ok], cls[ok], coefs[ok]
    xyxy = np.stack([cxcywh[:, 0] - cxcywh[:, 2] / 2, cxcywh[:, 1] - cxcywh[:, 3] / 2,
                     cxcywh[:, 0] + cxcywh[:, 2] / 2, cxcywh[:, 1] + cxcywh[:, 3] / 2], axis=1)
    if len(conf):
        m = nms(xyxy, conf, umbral_iou)
        xyxy, conf, cls, coefs = xyxy[m], conf[m], cls[m], coefs[m]
    return xyxy, conf, cls, coefs


def construir_mascara(coefs, protos, cajas, prep, tamano, max_lado=960):
    """Une las máscaras de todas las detecciones en UNA máscara booleana (alto, ancho).

    Resolución: la de la imagen original, reducida a `max_lado` px como máximo (así pesa poco).
    Los pasos replican a Ultralytics: coeficientes @ prototipos -> quitar el relleno del letterbox
    -> escalar a la imagen -> umbral (logit > 0, es decir sigmoide > 0.5) -> recortar a la caja.
    """
    c, mh, mw = protos.shape
    f = min(1.0, max_lado / max(prep.ancho, prep.alto))
    ow, oh = max(1, round(prep.ancho * f)), max(1, round(prep.alto * f))

    nw, nh = round(prep.ancho * prep.escala), round(prep.alto * prep.escala)
    kx, ky = mw / tamano, mh / tamano
    x0, x1 = int(round(prep.pad_x * kx)), int(round((prep.pad_x + nw) * kx))
    y0, y1 = int(round(prep.pad_y * ky)), int(round((prep.pad_y + nh) * ky))
    x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)

    base = protos.reshape(c, -1).astype(np.float32)
    union = np.zeros((oh, ow), dtype=bool)
    for coef, caja in zip(coefs, cajas):
        logit = (coef.astype(np.float32) @ base).reshape(mh, mw)[y0:y1, x0:x1]
        redim = np.asarray(Image.fromarray(np.ascontiguousarray(logit)).resize((ow, oh), Image.BILINEAR))
        dentro = np.zeros_like(union)
        bx1, by1 = int(np.floor(caja.x1 * f)), int(np.floor(caja.y1 * f))
        bx2, by2 = int(np.ceil(caja.x2 * f)), int(np.ceil(caja.y2 * f))
        dentro[max(by1, 0):by2, max(bx1, 0):bx2] = True
        union |= (redim > 0) & dentro
    return union


def posprocesar_seg(salida, protos, prep, umbral_conf, umbral_iou, max_det, tamano, con_mascara=True):
    """Como `posprocesar`, pero además devuelve la máscara unida (o None si no hay detecciones)."""
    xyxy, conf, cls, coefs = decodificar_seg(salida, umbral_conf, umbral_iou)
    xyxy = a_imagen_original(xyxy, prep)
    orden = np.argsort(conf)[::-1][:max_det]
    cajas = [Caja(*map(float, xyxy[i]), float(conf[i]), int(cls[i])) for i in orden]
    mascara = construir_mascara(coefs[orden], protos, cajas, prep, tamano) if (cajas and con_mascara) else None
    return cajas, mascara
