"""Validación de archivos: se revisa el CONTENIDO real, no solo la extensión."""
import io

from PIL import Image, UnidentifiedImageError

from ia.config import Config
from .errores import ErrorAPI

Image.MAX_IMAGE_PIXELS = 50_000_000     # protege contra imágenes-bomba


def validar_imagen(datos: bytes, cfg: Config) -> Image.Image:
    if not datos:
        raise ErrorAPI(400, "ARCHIVO_VACIO", "El archivo está vacío.")
    if len(datos) > cfg.max_bytes_imagen:
        raise ErrorAPI(413, "ARCHIVO_GRANDE",
                       f"La imagen supera el máximo de {cfg.max_bytes_imagen // (1024 * 1024)} MB.")
    try:
        img = Image.open(io.BytesIO(datos))
        formato = img.format
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ErrorAPI(415, "ARCHIVO_INVALIDO", "El archivo no es una imagen válida (use JPG o PNG).")
    if formato not in cfg.formatos_ok:
        raise ErrorAPI(415, "FORMATO_NO_ADMITIDO", "Formato no admitido. Use JPG o PNG.")
    if max(img.size) > cfg.max_lado_px:
        raise ErrorAPI(422, "IMAGEN_DEMASIADO_GRANDE",
                       f"La imagen supera {cfg.max_lado_px} px por lado.")
    if min(img.size) < 32:
        raise ErrorAPI(422, "IMAGEN_DEMASIADO_PEQUENA", "La imagen es demasiado pequeña.")
    return img
