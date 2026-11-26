# EVALUACIÓN SIMULADA CON IA — NO ES UN RESULTADO SUS NI SUSTITUYE LA SESIÓN CON PERSONAS

Fecha: 2026-11-12 · Versión: qa-eff8883 · Base: capturas de `salidas/evidencias/navegador/20261112-002915/` (pantalla de análisis, resultado con región y resultado sin región; Chromium 1366x768). No se calcula puntaje SUS ni se llena `respuestas.csv`.
Tarea evaluada: "cargar una imagen e interpretar el resultado".

## Recorrido por perfil
| Perfil | ¿Completaría sin ayuda? | Dónde dudaría / qué confunde |
|---|---|---|
| 1. Médico gastroenterólogo | Probablemente sí | El recuadro verde invade las franjas oscuras laterales y no coincide con la zona real (desfase, DEF-04): dudaría de la fiabilidad. "Confianza promedio 87.3%" sin explicar qué mide. Nombre fijo "Juan S." en la cabecera. |
| 2. Estudiante de medicina | Sí | "Posibles regiones" vs "Región detectada" vs "Completado": tres etiquetas para estados parecidos. En la imagen sin región, "Completado" no dice que no hubo hallazgo (solo lo dice la línea pequeña). |
| 3. Investigador de IA | Sí | Echa en falta versión del modelo, umbral y tiempos en la pantalla de resultado (solo ve "812 ms"). |
| 4. Persona sin experiencia técnica | Con dudas | No queda claro qué hacer con el resultado; el botón "Guardar y volver al historial" no indica qué se guarda. El aviso está en gris pequeño al pie. |
| 5. Usuario con baja visión | Probablemente no | Textos secundarios gris claro y chips pequeños con contraste bajo (DEF-05); el borde del recuadro se pierde sobre la mucosa; texto de 10 a 11 px. |

## Hallazgos (heurísticas de Nielsen, severidad 0-4)
1. Recuadro de ROI desalineado y poco visible (H1 visibilidad del estado / H5 prevención de errores): 4.
2. Bajo contraste y tamaño pequeño del texto secundario y del aviso (H8 diseño estético y minimalista / accesibilidad): 3.
3. Estados con nombres distintos para lo mismo: "Región detectada", "Completado", "Posibles regiones" (H4 consistencia): 2.
4. Resultado sin región poco explícito en la etiqueta (H2 correspondencia con el mundo real): 2.
5. "Confianza" sin explicación (H10 ayuda y documentación): 2.
6. Botón "Guardar y volver al historial" ambiguo (H6 reconocer en lugar de recordar): 2.
7. Nombre de usuario fijo "Juan S." (registro de demostración sin backend) (H4 / H1): 2.
8. Sin forma de deshacer o cancelar un análisis ya iniciado (H3 control del usuario): 1.
9. El flujo de carga tiene pocas ayudas para formatos y tamaño máximo de archivo (H9 recuperación de errores): 1.

## Mejoras propuestas al `guion_sesion.md`
- Dividir la tarea en pasos medibles con tiempo: cargar una imagen, leer si hay región y su confianza, explicar el aviso. Registrar tiempo y errores por paso.
- Añadir una tercera imagen con ROI que el sistema no detecte, para observar cómo interpreta el participante la ausencia de detección.
- Preguntar con sus palabras qué significa "confianza" y qué haría después del resultado (sin sugerirlo).
- Incluir al menos un participante con baja visión o usar zoom del 200 %, y registrar el perfil (médico, estudiante, técnico, lego) en el CSV.
- Definir de antemano qué es "pedir ayuda" y quién observa; grabar la pantalla con consentimiento, sin datos personales.
- Evitar que el moderador use las palabras "ROI" o "clasificación" en las instrucciones.
