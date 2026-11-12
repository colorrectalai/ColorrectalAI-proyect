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
# copia tu modelo exportado en el Colab a modelos/best.onnx
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

## Despliegue (Render, plan gratis)
1. Sube el `.onnx` a **GitHub Releases** y copia el enlace de descarga y el SHA-256 de `registro_experimento.json`.
2. En Render crea un *Web Service* desde Docker y define `MODELO_URL`, `MODELO_SHA256` y `CORS_ORIGENES` (URL de GitHub Pages).
3. El plan gratis se duerme a los 15 min: la primera petición tarda; el frontend debe llamar a `/api/v1/salud` antes.
