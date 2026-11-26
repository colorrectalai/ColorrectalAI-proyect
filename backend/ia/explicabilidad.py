"""Filtro 4: explicabilidad visual.

Genera la imagen con la ROI dibujada (cuadro + confianza) como data-URL en base64.
El frontend puede mostrarla tal cual, o dibujar las cajas en su <canvas> con las
coordenadas normalizadas (0-1) que también devuelve la API.
"""
import base64
import io

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

VERDE = (0, 220, 120)
CIAN = (5, 197, 222)        # mismo color que la ROI de la interfaz


def superponer_roi(img, cajas, max_lado=960):
    img = img.convert("RGB")
    f = 1.0
    if max(img.size) > max_lado:                 # una imagen más pequeña pesa menos en el JSON
        f = max_lado / max(img.size)
        img = img.resize((int(img.width * f), int(img.height * f)), Image.BILINEAR)

    dib = ImageDraw.Draw(img)
    grosor = max(2, img.width // 200)
    for c in cajas:
        x1, y1, x2, y2 = c.x1 * f, c.y1 * f, c.x2 * f, c.y2 * f
        dib.rectangle([x1, y1, x2, y2], outline=VERDE, width=grosor)
        dib.rectangle([x1, max(0, y1 - 18), x1 + 44, max(18, y1)], fill=VERDE)
        dib.text((x1 + 4, max(0, y1 - 16)), f"{c.confianza * 100:.0f}%", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _data_url(img, formato, **opciones):
    buf = io.BytesIO()
    img.save(buf, format=formato, **opciones)
    tipo = "image/png" if formato == "PNG" else "image/jpeg"
    return f"data:{tipo};base64," + base64.b64encode(buf.getvalue()).decode()


def _capa_mascara(mascara):
    """Capa RGBA transparente: relleno cian semitransparente + contorno sólido."""
    alto, ancho = mascara.shape
    m = Image.fromarray(mascara.astype(np.uint8) * 255)
    g = max(1, ancho // 320)
    borde = np.asarray(ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(2 * g + 1)))) > 0
    rgba = np.zeros((alto, ancho, 4), dtype=np.uint8)
    rgba[mascara] = (*CIAN, 100)
    rgba[borde] = (*CIAN, 255)
    return Image.fromarray(rgba)


def mascara_blanco_negro(mascara):
    """Máscara binaria como PNG en escala de grises: blanco = región segmentada, negro = fondo."""
    m = Image.fromarray(mascara.astype(np.uint8) * 255)
    return _data_url(m, "PNG", optimize=True)


def superponer_mascara(img, cajas, mascara):
    """Devuelve (imagen con la máscara y la confianza, capa PNG transparente solo con la máscara).

    La capa tiene la misma proporción que la imagen original: el frontend puede ponerla encima
    de la foto al 100 % de ancho y alto y queda alineada. `mascara` viene de construir_mascara.
    """
    alto, ancho = mascara.shape
    f = ancho / img.width
    base = img.convert("RGB").resize((ancho, alto), Image.BILINEAR)
    capa = _capa_mascara(mascara)

    final = Image.alpha_composite(base.convert("RGBA"), capa).convert("RGB")
    dib = ImageDraw.Draw(final)
    for c in cajas:
        x1, y1 = c.x1 * f, c.y1 * f
        dib.rectangle([x1, max(0, y1 - 18), x1 + 44, max(18, y1)], fill=CIAN)
        dib.text((x1 + 4, max(0, y1 - 16)), f"{c.confianza * 100:.0f}%", fill=(0, 0, 0))
    return _data_url(final, "JPEG", quality=85), _data_url(capa, "PNG", optimize=True)
