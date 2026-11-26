"""API REST de inferencia de ColorrectalAI (FastAPI + Uvicorn).
 
Arrancar en local:   uvicorn api.main:app --reload
Documentación:       http://localhost:8000/docs
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
 
from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
 
from ia.adaptador_yolo import AdaptadorYOLO
from ia.config import cargar_config
from . import db
from .admision import Admision
from .errores import (ErrorAPI, manejar_error_api, manejar_error_interno,
                      manejar_http, manejar_validacion)
from .esquemas import EstadoSalud, RespuestaInferencia
from .servicio_inferencia import analizar
from .usuarios import router as router_usuarios
from .validacion import validar_imagen
 
log = logging.getLogger("colorrectalai.api")
logging.basicConfig(level=logging.INFO)
 
 
@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    cfg = app.state.cfg
    app.state.admision = Admision(cfg.max_concurrentes, cfg.espera_max_s)
 
    async def cargar():               # no bloquea el arranque: /salud responde "cargando"
        try:
            await run_in_threadpool(app.state.modelo.cargar)
        except Exception:
            log.exception("No se pudo cargar el modelo")
        # Esquema, datos iniciales y registro del modelo cargado (solo si hay DATABASE_URL).
        await run_in_threadpool(db.preparar, getattr(app.state.modelo, "sha256_real", "") or "",
                                cfg.version_modelo, cfg.url_modelo)
 
    tarea = asyncio.create_task(cargar())
    yield
    tarea.cancel()
 
 
def _ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)
 
 
def _datos_archivo(datos, img):
    """(formato, tamaño en bytes, ancho, alto) de lo recibido; None si aún no se pudo leer."""
    formato = (img.format or "").lower() if img is not None else None
    return (formato or None, len(datos) if datos is not None else None,
            img.width if img is not None else None, img.height if img is not None else None)
 
 
def crear_app(cfg=None, modelo=None) -> FastAPI:
    cfg = cfg or cargar_config()
    app = FastAPI(title="ColorrectalAI · API de inferencia", version="0.2.1",
                  description="Uso académico y experimental. No es un dispositivo médico.",
                  lifespan=ciclo_vida)
    app.state.cfg = cfg
    app.state.modelo = modelo or AdaptadorYOLO(cfg.ruta_modelo, cfg.url_modelo, cfg.sha256_modelo)
 
    app.add_middleware(CORSMiddleware, allow_origins=list(cfg.origenes_cors),
                       allow_methods=["GET", "POST"], allow_headers=["*"])
    app.add_exception_handler(ErrorAPI, manejar_error_api)
    app.add_exception_handler(RequestValidationError, manejar_validacion)
    app.add_exception_handler(StarletteHTTPException, manejar_http)
    app.add_exception_handler(Exception, manejar_error_interno)
 
    app.include_router(router_usuarios)

    @app.get("/api/v1/salud", response_model=EstadoSalud, tags=["estado"])
    def salud():
        m = app.state.modelo
        return EstadoSalud(estado="ok" if m.listo else "cargando", modelo_listo=m.listo,
                           modelo_version=cfg.version_modelo, modelo_sha256=m.sha256_real,
                           base_datos=db.estado())
 
    @app.post("/api/v1/inferencias", response_model=RespuestaInferencia, tags=["inferencia"])
    async def inferir(imagen: UploadFile = File(..., description="JPG o PNG")):
        t0 = time.perf_counter()
        sha = app.state.modelo.sha256_real
        datos = img = None
        try:
            app.state.admision.entrar(app.state.modelo.listo)
            datos = await imagen.read(cfg.max_bytes_imagen + 1)
            img = validar_imagen(datos, cfg)
            async with app.state.admision.cupo():
                respuesta = await run_in_threadpool(analizar, img, app.state.modelo, cfg)
        except Exception as e:           # registro operacional (opcional, solo si hay base de datos)
            codigo = e.codigo if isinstance(e, ErrorAPI) else "ERROR_INTERNO"
            await db.registrar(_ms(t0), [], codigo, sha, *_datos_archivo(datos, img))
            raise
        await db.registrar(respuesta.metricas.latencia_ms, respuesta.rois, None, sha, *_datos_archivo(datos, img))
        return respuesta
 
    @app.get("/probar", response_class=HTMLResponse, include_in_schema=False)
    def pagina_de_prueba():
        """Página sencilla para ver el resultado con la ROI dibujada (solo desarrollo)."""
        return Path(__file__).with_name("probar.html").read_text(encoding="utf-8")
 
    return app
 
 
app = crear_app()
 