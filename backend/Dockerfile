FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY ia ./ia
# El modelo NO va en la imagen: se descarga de GitHub Releases al iniciar (MODELO_URL)
# y se verifica con MODELO_SHA256.
RUN useradd -m app && mkdir -p modelos && chown -R app /app
USER app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
