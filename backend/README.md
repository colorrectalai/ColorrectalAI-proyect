# ColorrectalAI · Backend (API de inferencia)

Proyecto académico y experimental (Universidad Santiago de Cali). **No es un dispositivo médico.**

```
api/   capa de servicio: rutas, validación, admisión (503), esquemas, errores en JSON
ia/    capa de IA: preprocesamiento → adaptador YOLO (ONNX Runtime) → posprocesamiento → explicabilidad
tests/ pytest con un modelo falso (no necesita el .onnx real)
```

## Correr en local
```sh
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                   # (o exporta las variables)
# copia el modelo de segmentación exportado a modelos/best_seg.onnx
uvicorn api.main:app --reload
pytest -q
```
Documentación interactiva: http://localhost:8000/docs

## Endpoints
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/v1/salud` | `ok` / `cargando`, versión y SHA-256 del modelo |
| POST | `/api/v1/inferencias` | multipart, campo `imagen` (JPG/PNG). Devuelve ROI, clasificación, confianza, imagen con la ROI y latencias |

Errores: `{"error": {"codigo": "...", "mensaje": "... en español"}}` con 400/413/415/422/503/500.

## Despliegue en Railway
1. Conecta el repositorio y configura la raíz del servicio como `/backend` para que Railway detecte este `Dockerfile`.
2. El Dockerfile incluye `modelos/best_seg.onnx`; por eso no necesitas definir `MODELO_URL` si usas el modelo del repositorio.
3. Configura `CORS_ORIGENES` con el dominio público del frontend. `MODELO_URL` y `MODELO_SHA256` quedan disponibles si luego quieres descargar y verificar un modelo externo.
