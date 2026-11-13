"""Filtro 4: explicabilidad visual.

Genera la imagen con la ROI dibujada (cuadro + confianza) como data-URL en base64.
El frontend puede mostrarla tal cual, o dibujar las cajas en su <canvas> con las
coordenadas normalizadas (0-1) que también devuelve la API.
"""
import base64
import io

from PIL import Image, ImageDraw

VERDE = (0, 220, 120)


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
