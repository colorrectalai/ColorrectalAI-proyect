"""Filtro 2: preprocesamiento (normalización y redimensionamiento).

Replica el 'letterbox' de Ultralytics: se conserva la proporción de la imagen y se
rellena con gris (114) hasta quedar cuadrada de tamano x tamano.
"""
from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class Preparada:
    tensor: np.ndarray      # (1, 3, T, T) float32 en [0, 1]
    ancho: int              # tamaño de la imagen original
    alto: int
    escala: float
    pad_x: float
    pad_y: float


def preprocesar(img: Image.Image, tamano: int) -> Preparada:
    img = img.convert("RGB")
    w, h = img.size
    escala = min(tamano / w, tamano / h)
    nw, nh = int(round(w * escala)), int(round(h * escala))
    redim = img.resize((nw, nh), Image.BILINEAR)

    lienzo = Image.new("RGB", (tamano, tamano), (114, 114, 114))
    pad_x, pad_y = (tamano - nw) // 2, (tamano - nh) // 2
    lienzo.paste(redim, (pad_x, pad_y))

    arr = np.asarray(lienzo, dtype=np.float32) / 255.0           # HWC
    tensor = np.ascontiguousarray(arr.transpose(2, 0, 1)[None])  # 1,3,H,W
    return Preparada(tensor, w, h, escala, float(pad_x), float(pad_y))
