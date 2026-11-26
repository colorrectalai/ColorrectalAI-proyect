-- ============================================================
-- ColorrectalAI | Datos iniciales (idempotente)
-- La API lo aplica al arrancar, después de 01_esquema.sql.
-- Contiene solo catálogos y el registro del experimento baseline
-- (entrenamiento/registro_experimento.json). Nada de pacientes ni imágenes.
-- La versión del modelo que esté desplegada se registra sola al arrancar
-- (api/db.py, a partir del SHA-256 de los pesos cargados).
-- ============================================================

BEGIN;

-- Clase que detecta el modelo
INSERT INTO clase_deteccion (nombre, descripcion)
VALUES ('polipo', 'Posible pólipo (clasificación experimental, no diagnóstica)')
ON CONFLICT (nombre) DO NOTHING;

-- Catálogo de errores que puede devolver la API (api/validacion.py, api/admision.py, api/errores.py)
INSERT INTO catalogo_error (codigo_interno, codigo_http, mensaje_es) VALUES
    ('ARCHIVO_VACIO',            400, 'El archivo está vacío.'),
    ('ARCHIVO_GRANDE',           413, 'La imagen supera el tamaño máximo permitido.'),
    ('ARCHIVO_INVALIDO',         415, 'El archivo no es una imagen válida (use JPG o PNG).'),
    ('FORMATO_NO_ADMITIDO',      415, 'Formato no admitido. Use JPG o PNG.'),
    ('IMAGEN_DEMASIADO_GRANDE',  422, 'La imagen supera el máximo de píxeles por lado.'),
    ('IMAGEN_DEMASIADO_PEQUENA', 422, 'La imagen es demasiado pequeña.'),
    ('SOLICITUD_INVALIDA',       422, 'La solicitud no es válida.'),
    ('RUTA_NO_ENCONTRADA',       404, 'La ruta solicitada no existe.'),
    ('METODO_NO_PERMITIDO',      405, 'Método no permitido para esta ruta.'),
    ('ERROR_HTTP',               400, 'No se pudo procesar la solicitud.'),
    ('MODELO_NO_LISTO',          503, 'El modelo aún se está cargando.'),
    ('SIN_CUPO',                 503, 'El servicio está ocupado.'),
    ('ERROR_INTERNO',            500, 'Ocurrió un error interno al procesar la imagen.')
ON CONFLICT (codigo_interno) DO NOTHING;

-- Métricas que se registran en las evaluaciones
INSERT INTO metrica (nombre, descripcion) VALUES
    ('precision_det',  'Precisión de detección (cajas)'),
    ('recall_det',     'Exhaustividad de detección (cajas)'),
    ('mAP50',          'mAP@0.5 de detección'),
    ('mAP50_95',       'mAP@0.5:0.95 de detección'),
    ('sensibilidad',   'Sensibilidad por imagen'),
    ('especificidad',  'Especificidad por imagen'),
    ('precision_img',  'Precisión por imagen'),
    ('F1',             'F1 por imagen'),
    ('ROC_AUC',        'Área bajo la curva ROC'),
    ('PR_AUC',         'Área bajo la curva precisión-exhaustividad'),
    ('brier',          'Brier Score (calibración)'),
    ('ECE',            'Error de calibración esperado'),
    ('Dice',           'Coeficiente de Dice (segmentación)'),
    ('IoU',            'Intersección sobre unión (segmentación)')
ON CONFLICT (nombre) DO NOTHING;

-- Responsable de los experimentos (sin datos personales)
INSERT INTO investigador (nombre_completo, correo, rol_equipo)
SELECT 'Equipo System Force', NULL, 'Equipo del proyecto'
WHERE NOT EXISTS (SELECT 1 FROM investigador WHERE nombre_completo = 'Equipo System Force');

-- Centros de PolypGen y partición usada en el baseline (por centro: C1-C4 / C5 / C6)
INSERT INTO centro_origen (id_dataset, codigo_centro, descripcion)
SELECT d.id_dataset, c.codigo, 'Centro ' || c.codigo || ' de PolypGen'
FROM dataset d CROSS JOIN (VALUES ('C1'),('C2'),('C3'),('C4'),('C5'),('C6')) AS c(codigo)
WHERE d.nombre = 'PolypGen' AND d.version = '1.0'
ON CONFLICT (id_dataset, codigo_centro) DO NOTHING;

INSERT INTO particion_dataset (id_dataset, nombre, criterio, semilla)
SELECT d.id_dataset, 'centros_C1-C4_C5_C6', 'por_centro', 42
FROM dataset d WHERE d.nombre = 'PolypGen' AND d.version = '1.0'
ON CONFLICT (id_dataset, nombre) DO NOTHING;

-- Experimento baseline (entrenamiento/registro_experimento.json)
INSERT INTO experimento (id_investigador, id_particion, nombre, entorno, framework,
                         hiperparametros, semilla, fecha_inicio, estado)
SELECT i.id_investigador, p.id_particion, 'baseline YOLO deteccion', 'Google Colab (GPU)',
       'Ultralytics 8.4.208 / PyTorch 2.14.1',
       '{"modelo_base": "yolo26n.pt", "epocas": 10, "tamano_img": 640, "umbral_confianza": 0.25}'::jsonb,
       42, TIMESTAMP '2026-11-10 08:22:30', 'finalizado'
FROM investigador i, particion_dataset p
WHERE i.nombre_completo = 'Equipo System Force' AND p.nombre = 'centros_C1-C4_C5_C6'
  AND NOT EXISTS (SELECT 1 FROM experimento WHERE nombre = 'baseline YOLO deteccion');

INSERT INTO version_modelo (id_experimento, nombre, version, formato, sha256_pesos, url_release,
                            tamano_mb, fecha_publicacion, estado)
SELECT e.id_experimento, 'ColorrectalAI YOLO', 'baseline-0.1', 'onnx',
       'b4c98b3538b28f2f22e7fbe6eaabff05662ad70cc9556de45bf881127a2410f3',
       'https://github.com/colorrectalai/ColorrectalAI-proyect/releases/tag/v0.1.0',
       NULL, TIMESTAMP '2026-11-12 06:32:09', 'retirado'
FROM experimento e WHERE e.nombre = 'baseline YOLO deteccion'
ON CONFLICT DO NOTHING;

-- Evaluación del baseline sobre el centro de prueba (C6), umbral 0.25
INSERT INTO evaluacion (id_modelo, subconjunto, umbral_confianza, fecha)
SELECT vm.id_modelo, 'prueba', 0.250, TIMESTAMP '2026-11-10 08:22:30'
FROM version_modelo vm WHERE vm.version = 'baseline-0.1'
ON CONFLICT (id_modelo, subconjunto, umbral_confianza) DO NOTHING;

INSERT INTO evaluacion_metrica (id_evaluacion, id_metrica, valor)
SELECT ev.id_evaluacion, m.id_metrica, v.valor
FROM evaluacion ev
JOIN version_modelo vm ON vm.id_modelo = ev.id_modelo AND vm.version = 'baseline-0.1'
JOIN (VALUES ('precision_det', 0.826101), ('recall_det', 0.626398), ('mAP50', 0.727702),
             ('mAP50_95', 0.542037), ('sensibilidad', 0.837800), ('especificidad', 0.787600),
             ('precision_img', 0.934200), ('F1', 0.883400), ('ROC_AUC', 0.900900),
             ('PR_AUC', 0.970800), ('brier', 0.182900), ('ECE', 0.256300)) AS v(nombre, valor)
  ON TRUE
JOIN metrica m ON m.nombre = v.nombre
WHERE ev.subconjunto = 'prueba'
ON CONFLICT (id_evaluacion, id_metrica) DO NOTHING;

COMMIT;
