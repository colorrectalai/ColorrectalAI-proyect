"""Servicio de inferencia: coordina la tubería de filtros (en memoria, sin guardar nada)."""
import time
import uuid

from PIL import Image

from ia.adaptador_yolo import AdaptadorYOLO
from ia.config import Config
from ia.explicabilidad import superponer_roi
from ia.posprocesamiento import posprocesar
from ia.preprocesamiento import preprocesar
from .esquemas import Metricas, ROI, RespuestaInferencia


def _ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)


def analizar(img: Image.Image, modelo: AdaptadorYOLO, cfg: Config,
             con_imagen: bool = True) -> RespuestaInferencia:
    t_total = time.perf_counter()

    t = time.perf_counter()
    prep = preprocesar(img, modelo.tamano_entrada)
    t_pre = _ms(t)

    t = time.perf_counter()
    salida = modelo.ejecutar(prep.tensor)
    t_inf = _ms(t)

    t = time.perf_counter()
    cajas = posprocesar(salida, prep, cfg.umbral_conf, cfg.umbral_iou, cfg.max_detecciones)
    rois = [ROI(x=c.x1 / prep.ancho, y=c.y1 / prep.alto,
                ancho=(c.x2 - c.x1) / prep.ancho, alto=(c.y2 - c.y1) / prep.alto,
                confianza=min(max(c.confianza, 0.0), 1.0)) for c in cajas]
    imagen = superponer_roi(img, cajas) if (con_imagen and cajas) else None
    t_pos = _ms(t)

    return RespuestaInferencia(
        id=uuid.uuid4().hex[:12],
        clasificacion="posible_region" if cajas else "sin_hallazgos",
        confianza=max((r.confianza for r in rois), default=0.0),
        rois=rois, imagen_ancho=prep.ancho, imagen_alto=prep.alto, imagen_resultado=imagen,
        metricas=Metricas(latencia_ms=_ms(t_total), preprocesamiento_ms=t_pre,
                          inferencia_ms=t_inf, posprocesamiento_ms=t_pos),
        modelo_version=cfg.version_modelo, aviso=cfg.aviso)
