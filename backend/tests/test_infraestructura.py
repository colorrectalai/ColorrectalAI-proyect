"""Configuración, despliegue y documentación: que lo que el código necesita esté declarado."""
import json
import pathlib
import re

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BACK = RAIZ / "backend"


def variables_usadas():
    fuente = "".join(p.read_text(encoding="utf-8") for p in (BACK / "api").glob("*.py"))
    fuente += "".join(p.read_text(encoding="utf-8") for p in (BACK / "ia").glob("*.py"))
    return set(re.findall(r'_env\("([A-Z_]+)"', fuente)) | set(re.findall(r'os\.getenv\("([A-Z_]+)"', fuente))


@pytest.mark.parametrize("var", sorted(variables_usadas() - {"ONNX_HILOS"}))
def test_cada_variable_de_entorno_esta_documentada(var):
    assert re.search(rf"^{var}=", (BACK / ".env.example").read_text(encoding="utf-8"), re.M)


@pytest.mark.parametrize("carpeta", ["api", "ia", "db", "modelos"])
def test_dockerfile_copia_lo_necesario(carpeta):
    assert f"COPY {carpeta} ./{carpeta}" in (BACK / "Dockerfile").read_text()


def test_dockerfile_no_corre_como_root_y_usa_el_puerto_de_railway():
    d = (BACK / "Dockerfile").read_text()
    assert "USER app" in d and "${PORT:-8000}" in d


@pytest.mark.parametrize("modulo", ["backend", "frontend", "database", "entrenamiento"])
def test_cada_modulo_tiene_readme(modulo):
    assert any((RAIZ / modulo).glob("README*"))


def test_env_y_secretos_no_se_versionan():
    gi = (RAIZ / ".gitignore").read_text()
    assert ".env" in gi


def test_dependencias_principales_fijadas():
    req = (BACK / "requirements.txt").read_text()
    for paquete in ("fastapi", "uvicorn", "pydantic", "onnxruntime"):
        assert re.search(rf"^{paquete}(\[.*\])?==", req, re.M), paquete


def test_registro_del_experimento_tiene_lo_necesario_para_reproducir():
    reg = json.loads((RAIZ / "entrenamiento" / "registro_experimento.json").read_text(encoding="utf-8"))
    for clave in ("semilla", "epocas", "tamano_img", "versiones", "division_por_centro", "onnx"):
        assert clave in reg
    assert len(reg["onnx"]["sha256"]) == 64


def test_modelo_desplegado_esta_en_el_repositorio():
    assert (BACK / "modelos" / "best_seg.onnx").stat().st_size > 1_000_000
