// Utilidades para montar vistas con el router real de la aplicación.
import { flushPromises, mount } from '@vue/test-utils'
import router from '../../src/router'

export async function montar(componente, ruta = '/', opciones = {}) {
  await router.push(ruta)
  await router.isReady()
  const w = mount(componente, { global: { plugins: [router] }, attachTo: document.body, ...opciones })
  await flushPromises()
  return w
}

export const respuestaApi = (extra = {}) => ({
  id: 'abc123def456', clasificacion: 'posible_region', confianza: 0.91,
  rois: [{ x: 0.2, y: 0.3, ancho: 0.25, alto: 0.2, confianza: 0.91 }],
  imagen_ancho: 800, imagen_alto: 600, imagen_resultado: null,
  mascara_resultado: 'data:image/png;base64,AAA', mascara_bn: 'data:image/png;base64,BBB',
  metricas: { latencia_ms: 500, preprocesamiento_ms: 20, inferencia_ms: 120, posprocesamiento_ms: 360 },
  modelo_version: 'seg-0.1', aviso: 'Resultado experimental con fines académicos. No constituye un diagnóstico médico.',
  ...extra,
})

export const archivo = (nombre, tipo = 'image/png', bytes = 10) => new File([new Uint8Array(bytes)], nombre, { type: tipo })
export { flushPromises, router }
