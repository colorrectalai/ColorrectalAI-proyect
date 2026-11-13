"""Configuración y versiones del motor de IA (módulo 'Config. y versiones').

Todo se puede cambiar con variables de entorno, sin tocar el código.
"""
import os
from dataclasses import dataclass, field


def _env(nombre: str, defecto, tipo=str):
    return tipo(os.getenv(nombre, defecto))


@dataclass(frozen=True)
class Config:
    # --- Modelo ---
    ruta_modelo: str = field(default_factory=lambda: _env("MODELO_RUTA", "modelos/best.onnx"))
    # Si el archivo no existe, se descarga de GitHub Releases (URL del asset .onnx).
    url_modelo: str = field(default_factory=lambda: _env("MODELO_URL", ""))
    sha256_modelo: str = field(default_factory=lambda: _env("MODELO_SHA256", "").lower())
    version_modelo: str = field(default_factory=lambda: _env("MODELO_VERSION", "baseline-0.1"))

    # --- Inferencia (mismos valores que el Colab) ---
    tamano_img: int = field(default_factory=lambda: _env("TAMANO_IMG", 640, int))
    umbral_conf: float = field(default_factory=lambda: _env("UMBRAL_CONF", 0.25, float))
    umbral_iou: float = field(default_factory=lambda: _env("UMBRAL_IOU", 0.45, float))
    max_detecciones: int = field(default_factory=lambda: _env("MAX_DETECCIONES", 20, int))

    # --- Admisión y validación ---
    max_concurrentes: int = field(default_factory=lambda: _env("MAX_CONCURRENTES", 2, int))
    max_bytes_imagen: int = field(default_factory=lambda: _env("MAX_MB_IMAGEN", 8, int) * 1024 * 1024)
    max_lado_px: int = field(default_factory=lambda: _env("MAX_LADO_PX", 6000, int))
    formatos_ok: tuple = ("JPEG", "PNG")

    # --- CORS: URL(s) del frontend separadas por coma ---
    origenes_cors: tuple = field(default_factory=lambda: tuple(
        o.strip() for o in _env("CORS_ORIGENES", "http://localhost:5173").split(",") if o.strip()))

    aviso: str = ("Resultado experimental con fines académicos. "
                  "No constituye un diagnóstico médico.")


def cargar_config() -> Config:
    return Config()
