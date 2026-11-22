"""Esquemas de respuesta (Pydantic): este es el CONTRATO con el frontend."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ROI(BaseModel):
    # Coordenadas normalizadas 0-1 respecto a la imagen original (fáciles de dibujar en <canvas>)
    x: float = Field(description="Esquina izquierda")
    y: float = Field(description="Esquina superior")
    ancho: float
    alto: float
    confianza: float = Field(ge=0, le=1)


class Metricas(BaseModel):
    latencia_ms: float
    preprocesamiento_ms: float
    inferencia_ms: float
    posprocesamiento_ms: float


class RespuestaInferencia(BaseModel):
    id: str
    clasificacion: Literal["posible_region", "sin_hallazgos"]
    confianza: float = Field(ge=0, le=1, description="Confianza de la caja más segura (0 si no hay)")
    rois: list[ROI]
    imagen_ancho: int
    imagen_alto: int
    imagen_resultado: Optional[str] = Field(None, description="data-URL con la ROI (o la máscara) dibujada")
    mascara_resultado: Optional[str] = Field(
        None, description="data-URL PNG transparente con solo la máscara (modelo de segmentación); "
                          "misma proporción que la imagen original, para superponerla al 100 %")
    mascara_bn: Optional[str] = Field(
        None, description="data-URL PNG en blanco y negro (blanco = región segmentada, negro = fondo); "
                          "misma proporción que la imagen original. Solo con modelo de segmentación")
    metricas: Metricas
    modelo_version: str
    aviso: str


class EstadoSalud(BaseModel):
    estado: Literal["ok", "cargando"]
    modelo_listo: bool
    modelo_version: str
    modelo_sha256: str
    base_datos: Literal["no_configurada", "conectada", "sin_conexion"] = "no_configurada"
