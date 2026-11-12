"""Filtro 3: posprocesamiento.

Convierte la salida cruda del ONNX en cajas sobre la imagen ORIGINAL.
Soporta los dos formatos que produce Ultralytics:
  A) end-to-end (YOLO26, NMS integrado):  (1, N, 6) -> x1, y1, x2, y2, conf, clase
  B) clásico (YOLOv8 / YOLO11):           (1, 4+nc, anclas) -> cx, cy, w, h, conf_clase...
Si tu .onnx muestra otra forma en `inspeccionar_onnx` del Colab, solo hay que tocar aquí.
"""
from dataclasses import dataclass

import numpy as np


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
