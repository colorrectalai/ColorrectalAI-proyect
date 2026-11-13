"""Adaptador del modelo YOLO: aísla al resto del sistema del formato ONNX.

Carga el modelo UNA vez (al iniciar), verifica su SHA-256 y ejecuta la inferencia en CPU.
"""
import hashlib
import logging
import os
import urllib.request

import numpy as np
import onnxruntime as ort

log = logging.getLogger("colorrectalai.ia")


def sha256_archivo(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


class AdaptadorYOLO:
    def __init__(self, ruta: str, url: str = "", sha256_esperado: str = ""):
        self.ruta = ruta
        self.url = url
        self.sha256_esperado = sha256_esperado
        self.sha256_real = ""
        self.sesion = None
        self.entrada = ""
        self.tamano_entrada = 640

    @property
    def listo(self) -> bool:
        return self.sesion is not None

    def cargar(self) -> None:
        if not os.path.exists(self.ruta):
            if not self.url:
                raise FileNotFoundError(f"No existe {self.ruta} y MODELO_URL está vacío")
            os.makedirs(os.path.dirname(self.ruta) or ".", exist_ok=True)
            log.info("Descargando el modelo desde GitHub Releases...")
            urllib.request.urlretrieve(self.url, self.ruta)

        self.sha256_real = sha256_archivo(self.ruta)
        if self.sha256_esperado and self.sha256_real != self.sha256_esperado:
            raise ValueError("El SHA-256 del modelo no coincide con el publicado")

        opciones = ort.SessionOptions()
        opciones.intra_op_num_threads = int(os.getenv("ONNX_HILOS", "1"))
        self.sesion = ort.InferenceSession(
            self.ruta, sess_options=opciones, providers=["CPUExecutionProvider"])
        entrada = self.sesion.get_inputs()[0]
        self.entrada = entrada.name
        if isinstance(entrada.shape[2], int):
            self.tamano_entrada = entrada.shape[2]
        log.info("Modelo cargado: entrada=%s %s", self.entrada, entrada.shape)

    def ejecutar(self, tensor: np.ndarray) -> np.ndarray:
        """Devuelve la salida cruda del modelo (primer tensor de salida)."""
        return self.sesion.run(None, {self.entrada: tensor})[0]
