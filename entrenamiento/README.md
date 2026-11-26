# Entrenamiento del modelo (YOLO + PolypGen)

## Propósito

Entrenar y evaluar el detector de pólipos de ColorrectalAI con el dataset público PolypGen, exportarlo a
ONNX para el backend y dejar el registro necesario para que otra persona reproduzca el resultado.
Uso académico y experimental: los resultados no constituyen un diagnóstico médico.

## Contenido

| Archivo | Qué es |
|---|---|
| `ColorrectalAI_YOLO_ajustado.ipynb` | Cuaderno de Google Colab: prepara PolypGen, entrena, evalúa, exporta a ONNX y genera el registro. |
| `registro_experimento.json` | Registro del experimento baseline: semilla, versiones, partición, métricas y SHA-256 del ONNX. |
| `requirements-entrenamiento.txt` | Versiones exactas usadas en el entrenamiento registrado. |
| `registro_reproduccion.md` | Planilla para anotar la reproducción hecha por otro integrante (CP-16). |

## Entradas

- **Dataset:** PolypGen (Ali et al., 2023), descargado de Synapse. Licencia CC BY 4.0: hay que citarlo.
  El cuaderno espera el zip en Google Drive (`RUTA_POLYPGEN`, celda de configuración).
- **Modelo base:** `yolo26n.pt` (Ultralytics), se descarga solo.
- **Configuración** (celda 0 del cuaderno): `SEMILLA = 42`, `TAMANO_IMG = 640`, `EPOCAS`, umbral 0.25 y
  partición **por centro**: entrenamiento C1–C4, validación C5, prueba C6. Ningún paciente queda en
  dos grupos, porque cada paciente pertenece a un solo centro.

## Salidas

- `best.pt` y `best.onnx` (entrada fija 1×3×640×640) con su SHA-256.
- Métricas de detección (precisión, recall, mAP@0.5, mAP@0.5:0.95) y por imagen (sensibilidad,
  especificidad, F1, ROC-AUC, PR-AUC, Brier, ECE) sobre el centro de prueba C6.
- `registro_experimento.json` y `modelo_para_backend.zip` (ONNX + registro) para copiar a `backend/modelos/`.

## Cómo ejecutarlo

1. Abrir el cuaderno en Google Colab con GPU (*Entorno de ejecución → Cambiar tipo → T4 GPU*).
2. Subir PolypGen a Google Drive y poner su ruta en `RUTA_POLYPGEN`.
3. Ejecutar las celdas en orden. La Parte 1 solo comprueba que YOLO funciona; el entrenamiento real es la Parte 2.
4. Revisar la comprobación visual (2.4) antes de entrenar: las cajas deben rodear los pólipos.
5. Al final, descargar `modelo_para_backend.zip`.

## Reproducir el baseline registrado (CP-16, RNF-018.1)

Lo hace un integrante **distinto** de quien entrenó, siguiendo solo esta guía:

1. Usar las versiones de `requirements-entrenamiento.txt` (en Colab:
   `!pip install -q -r requirements-entrenamiento.txt` en lugar de la celda de instalación).
2. En la configuración dejar `SEMILLA = 42`, `TAMANO_IMG = 640` y **`EPOCAS = 10`**, que es lo que dice
   `registro_experimento.json` (el valor por defecto del cuaderno es 50).
3. Ejecutar la Parte 2 completa y anotar el mAP@0.5 obtenido en `registro_reproduccion.md`.
4. Criterio: |mAP@0.5 obtenido − 0.7277| ≤ 0.02.

## Modelo desplegado actualmente

La API usa el modelo de **segmentación `seg-0.1`** (`backend/modelos/best_seg.onnx`,
SHA-256 `61bec40566c15624f8319af8e9da197a06c24424f51c7956e21d70ef632ef603`), publicado en el
Release `v0.2.0`. **Pendiente:** subir aquí su cuaderno de entrenamiento y su `registro_experimento.json`
(semilla, épocas, métricas Dice/IoU). Sin ellos, el modelo desplegado no se puede reproducir.
