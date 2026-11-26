"""Capa de IA: preprocesamiento, IoU/NMS, decodificación, coordenadas, máscaras, explicabilidad,
carga del modelo y servicio de inferencia."""
import base64
import hashlib
import io

import numpy as np
import pytest
from PIL import Image

from api.servicio_inferencia import analizar
from ia.adaptador_yolo import AdaptadorYOLO, sha256_archivo
from ia.config import Config
from ia.explicabilidad import mascara_blanco_negro, superponer_mascara, superponer_roi
from ia.posprocesamiento import (Caja, _iou, a_imagen_original, construir_mascara, decodificar,
                                 decodificar_seg, nms, posprocesar)
from ia.preprocesamiento import preprocesar
from tests.conftest import ModeloFalso, ModeloFalsoSeg


def img(w, h, color=(120, 60, 60)):
    return Image.new("RGB", (w, h), color)


def decodificar_data_url(url):
    cab, datos = url.split(",", 1)
    return cab, Image.open(io.BytesIO(base64.b64decode(datos)))


# ---------------- Preprocesamiento (letterbox) ----------------
@pytest.mark.parametrize("w,h", [(640, 640), (1280, 720), (720, 1280), (100, 50), (33, 2000)])
def test_preprocesar_forma_tipo_y_rango(w, h):
    p = preprocesar(img(w, h), 640)
    assert p.tensor.shape == (1, 3, 640, 640) and p.tensor.dtype == np.float32
    assert 0.0 <= p.tensor.min() and p.tensor.max() <= 1.0
    assert (p.ancho, p.alto) == (w, h)


@pytest.mark.parametrize("w,h", [(1280, 720), (720, 1280)])
def test_letterbox_conserva_proporcion_y_centra(w, h):
    p = preprocesar(img(w, h), 640)
    assert p.escala == pytest.approx(min(640 / w, 640 / h))
    assert (p.pad_x == 0) or (p.pad_y == 0)
    gris = p.tensor[0, :, 0, 0] if p.pad_y else p.tensor[0, :, 0, 0]
    if p.pad_x or p.pad_y:
        assert np.allclose(gris, 114 / 255, atol=1e-3)            # el relleno es gris 114


@pytest.mark.parametrize("modo", ["L", "RGBA", "P", "CMYK"])
def test_preprocesar_convierte_cualquier_modo_a_rgb(modo):
    assert preprocesar(Image.new(modo, (64, 64)), 640).tensor.shape[1] == 3


# ---------------- IoU y NMS ----------------
def test_iou_cajas_iguales_y_disjuntas():
    a = np.array([0, 0, 10, 10], dtype=float)
    b = np.array([[0, 0, 10, 10], [20, 20, 30, 30], [5, 0, 15, 10]], dtype=float)
    r = _iou(a, b)
    assert r[0] == pytest.approx(1.0) and r[1] == pytest.approx(0.0) and r[2] == pytest.approx(1 / 3, rel=1e-3)


def test_nms_elimina_solapadas_y_conserva_la_mejor():
    cajas = np.array([[0, 0, 10, 10], [1, 1, 11, 11], [50, 50, 60, 60]], dtype=float)
    assert sorted(nms(cajas, np.array([0.9, 0.8, 0.7]), 0.45)) == [0, 2]


def test_nms_con_una_sola_caja():
    assert nms(np.array([[0, 0, 1, 1]], dtype=float), np.array([0.5]), 0.45) == [0]


# ---------------- Decodificación ----------------
def test_decodificar_formato_end_to_end_filtra_por_umbral():
    s = np.zeros((1, 300, 6), dtype=np.float32)
    s[0, 0] = [10, 10, 50, 50, 0.9, 0]
    s[0, 1] = [10, 10, 50, 50, 0.1, 0]
    xyxy, conf, cls = decodificar(s, 0.25, 0.45)
    assert len(conf) == 1 and conf[0] == pytest.approx(0.9)


def test_decodificar_formato_clasico_aplica_nms():
    s = np.zeros((1, 5, 8400), dtype=np.float32)
    s[0, :, 0] = [100, 100, 40, 40, 0.9]
    s[0, :, 1] = [102, 101, 40, 40, 0.8]        # casi igual: NMS la elimina
    xyxy, conf, _ = decodificar(s, 0.25, 0.45)
    assert len(conf) == 1 and xyxy[0].tolist() == pytest.approx([80, 80, 120, 120])


def test_decodificar_sin_detecciones():
    xyxy, conf, _ = decodificar(np.zeros((1, 300, 6), dtype=np.float32), 0.25, 0.45)
    assert len(conf) == 0


def test_a_imagen_original_deshace_letterbox_y_recorta():
    p = preprocesar(img(1280, 720), 640)
    out = a_imagen_original([[0, p.pad_y, 640, 640 - p.pad_y], [-50, -50, 2000, 2000]], p)
    assert out[0].tolist() == pytest.approx([0, 0, 1280, 720], abs=1)
    assert out[1].tolist() == pytest.approx([0, 0, 1280, 720], abs=1)


def test_posprocesar_respeta_max_det_y_ordena_por_confianza():
    s = np.zeros((1, 300, 6), dtype=np.float32)
    for i, c in enumerate([0.3, 0.9, 0.6, 0.8]):
        s[0, i] = [10 * i, 10, 10 * i + 5, 15, c, 0]
    cajas = posprocesar(s, preprocesar(img(640, 640), 640), 0.25, 0.45, max_det=2)
    assert [round(c.confianza, 1) for c in cajas] == [0.9, 0.8]


def test_decodificar_seg_rechaza_forma_inesperada():
    with pytest.raises(ValueError):
        decodificar_seg(np.zeros((1, 20, 100), dtype=np.float32), 0.25, 0.45)


# ---------------- Máscaras y explicabilidad ----------------
def test_construir_mascara_dentro_de_la_caja_y_tamano_limitado():
    from tests.conftest import salida_seg_falsa
    det, protos = salida_seg_falsa()
    p = preprocesar(img(2000, 2000), 640)
    _, _, _, coefs = decodificar_seg(det, 0.25, 0.45)
    caja = Caja(200 / p.escala, 200 / p.escala, 400 / p.escala, 400 / p.escala, 0.9, 0)
    m = construir_mascara(coefs, protos, [caja], p, 640)
    assert m.dtype == bool and max(m.shape) <= 960 and m.any()
    ys, xs = np.nonzero(m)
    f = m.shape[1] / 2000
    assert xs.min() >= caja.x1 * f - 2 and xs.max() <= caja.x2 * f + 2


def test_mascara_blanco_negro_es_png_binario():
    m = np.zeros((40, 60), dtype=bool); m[10:20, 10:30] = True
    cab, im = decodificar_data_url(mascara_blanco_negro(m))
    assert cab.startswith("data:image/png") and set(np.unique(np.asarray(im))) <= {0, 255}


def test_superponer_mascara_devuelve_jpeg_y_capa_png_transparente():
    m = np.zeros((48, 64), dtype=bool); m[5:20, 5:20] = True
    jpg, capa = superponer_mascara(img(64, 48), [Caja(5, 5, 20, 20, 0.8, 0)], m)
    assert jpg.startswith("data:image/jpeg")
    _, c = decodificar_data_url(capa)
    assert c.mode == "RGBA" and c.size == (64, 48) and np.asarray(c)[0, 0, 3] == 0


@pytest.mark.parametrize("w,h", [(640, 480), (3000, 2000)])
def test_superponer_roi_reduce_imagenes_grandes(w, h):
    cab, im = decodificar_data_url(superponer_roi(img(w, h), [Caja(10, 10, 100, 100, 0.9, 0)]))
    assert cab.startswith("data:image/jpeg") and max(im.size) <= 960


# ---------------- Servicio de inferencia ----------------
def test_analizar_coherencia_de_la_respuesta():
    r = analizar(img(800, 600), ModeloFalso(), Config())
    assert r.clasificacion == "posible_region" and len(r.rois) == 1
    assert r.confianza == max(x.confianza for x in r.rois)
    for roi in r.rois:
        assert 0 <= roi.x <= 1 and 0 <= roi.y <= 1 and 0 < roi.ancho <= 1 and 0 < roi.alto <= 1
    assert r.aviso and "diagnóstico" in r.aviso and r.metricas.latencia_ms >= 0


def test_analizar_sin_hallazgos_no_trae_imagenes():
    r = analizar(img(800, 600), ModeloFalso(con_deteccion=False), Config())
    assert r.clasificacion == "sin_hallazgos" and r.confianza == 0 and r.imagen_resultado is None


def test_analizar_segmentacion_trae_las_dos_mascaras():
    r = analizar(img(640, 640), ModeloFalsoSeg(), Config())
    assert r.mascara_resultado.startswith("data:image/png") and r.mascara_bn.startswith("data:image/png")


def test_analizar_sin_imagen_no_genera_data_urls():
    r = analizar(img(640, 640), ModeloFalsoSeg(), Config(), con_imagen=False)
    assert r.imagen_resultado is None and r.mascara_bn is None and r.rois


def test_analizar_ids_unicos():
    ids = {analizar(img(64, 64), ModeloFalso(), Config()).id for _ in range(20)}
    assert len(ids) == 20


# ---------------- Carga y verificación del modelo ----------------
def test_sha256_archivo(tmp_path):
    f = tmp_path / "m.onnx"; f.write_bytes(b"pesos")
    assert sha256_archivo(str(f)) == hashlib.sha256(b"pesos").hexdigest()


def test_modelo_inexistente_sin_url_no_queda_listo(tmp_path):
    a = AdaptadorYOLO(str(tmp_path / "no.onnx"))
    with pytest.raises(FileNotFoundError):
        a.cargar()
    assert a.listo is False


def test_modelo_con_sha_distinto_se_rechaza(tmp_path):
    f = tmp_path / "m.onnx"; f.write_bytes(b"pesos-alterados")
    a = AdaptadorYOLO(str(f), sha256_esperado="0" * 64)
    with pytest.raises(ValueError):
        a.cargar()
    assert a.listo is False


def test_modelo_real_del_repo_carga_y_es_segmentacion():
    import os
    ruta = "modelos/best_seg.onnx"
    if not os.path.exists(ruta):
        pytest.skip("sin el modelo en el repositorio")
    a = AdaptadorYOLO(ruta)
    a.cargar()
    assert a.listo and a.es_segmentacion and a.tamano_entrada == 640
    assert a.sha256_real == "61bec40566c15624f8319af8e9da197a06c24424f51c7956e21d70ef632ef603"
