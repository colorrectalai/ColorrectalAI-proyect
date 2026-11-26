// API simulada con el contrato real y utilidades comunes de las pruebas de extremo a extremo.
export const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAKAAAAB4CAIAAAD6wG44AAAB/klEQVR4nO3cMU7DQBBGYYN8ib0BNQejziWh5gZzDQo6QBGKbO/8b9+rrWg0n0ZJYeXp/fa2Gbfn2QPYuQkMT2B4AsMTGJ7A8ASGJzA8geEJDE9geALDExiewPAEhicwPIHhCQxPYHgCwxMYnsDwBIYnMDyB4QkMT2B4AsMTGJ7A8ASGJzA8geEJDG/fcI3Xl/sP1Mfntkz7Oq6/n1xBel/HdU3pfU3aPz8KyZz6I+tA3VM/c3p5F3wqw8CdctgFX3NkA3TKScBX7n1QjGOAr9/4QBhnAM/a9cg3DgCeu+URbhwAbGTgDgc0GszABO6z2dFmEhSwkYG7Hc1oNk88sB2SwPAEhtcUuOcX3mg5VSSwHZXA8ASGJzA8geEJDE9geE2Be77XWC2nigS2oxIYnsDw+gJ3+8KrZvPEAxsfuM/RVJtJUMBNNlsNZsACGx947gFV8vlmAE/ccoXrxgBP2XXl6yYBX7zxQuiGAV+296LoRv5Hx/f2T3rBsUC0kRd8qkThdCMv+IxTLiJtPPAPmweki+vKAX5AuhZwBQKv6Yf9kWX/TGB4AsMTGJ7A8ASGJzA8geEJDE9geALDExiewPAEhicwPIHhCQxPYHgCwxMYnsDwBIYnMDyB4QkMT2B4AsMTGJ7A8ASGJzA8geEJDE9geALDExiewPAE3th9AZR2aESu3qweAAAAAElFTkSuQmCC', 'base64')
export const imagen = (nombre, marca = '') => ({ name: nombre, mimeType: 'image/png', buffer: Buffer.concat([PNG, Buffer.from(marca)]) })

export const respuesta = (extra = {}) => ({
  id: Math.random().toString(16).slice(2, 14), clasificacion: 'posible_region', confianza: 0.91,
  rois: [{ x: 0.3, y: 0.3, ancho: 0.35, alto: 0.4, confianza: 0.91 }], imagen_ancho: 160, imagen_alto: 120,
  imagen_resultado: null, mascara_resultado: 'data:image/png;base64,' + PNG.toString('base64'),
  mascara_bn: 'data:image/png;base64,' + PNG.toString('base64'),
  metricas: { latencia_ms: 500, preprocesamiento_ms: 20, inferencia_ms: 120, posprocesamiento_ms: 360 },
  modelo_version: 'seg-0.1', aviso: 'Resultado experimental con fines académicos. No constituye un diagnóstico médico.', ...extra,
})

// modo: 'normal' | 'caida' | 'error500'
export async function simularApi(page, modo = 'normal') {
  await page.route('http://api.prueba/**', async (route) => {
    const req = route.request(); const url = req.url()
    if (modo === 'caida') return route.abort('connectionrefused')
    if (modo === 'error500') return route.fulfill({ status: 500, json: { error: { codigo: 'ERROR_INTERNO', mensaje: 'Ocurrió un error interno al procesar la imagen.' } } })
    if (url.endsWith('/api/v1/inferencias')) {
      if ((req.postDataBuffer() || Buffer.alloc(0)).includes('RECHAZAR')) {
        return route.fulfill({ status: 415, json: { error: { codigo: 'FORMATO_NO_ADMITIDO', mensaje: 'Formato no admitido. Use JPG o PNG.' } } })
      }
      return route.fulfill({ json: respuesta() })
    }
    if (url.endsWith('/api/v1/usuarios')) {
      const d = req.postDataJSON()
      return route.fulfill({ status: 201, json: { token: 'a.b', tipo: 'bearer', expira_en_s: 3600, usuario: { id: 1, nombre: d.nombre, correo: d.correo } } })
    }
    if (url.endsWith('/api/v1/sesiones')) {
      const d = req.postDataJSON()
      if (d.contrasena !== 'ClaveSegura123') return route.fulfill({ status: 401, json: { error: { codigo: 'CREDENCIALES_INVALIDAS', mensaje: 'Correo o contraseña incorrectos.' } } })
      return route.fulfill({ json: { token: 'a.b', tipo: 'bearer', expira_en_s: 3600, usuario: { id: 1, nombre: 'Ana Ruiz', correo: d.correo } } })
    }
    return route.fulfill({ json: { estado: 'ok', modelo_listo: true, modelo_version: 'seg-0.1', modelo_sha256: 'x', base_datos: 'conectada' } })
  })
}

export async function analizar(page, archivos) {
  await page.goto('/carga')
  await page.locator('input[type="file"]').setInputFiles(archivos)
  await page.getByRole('button', { name: /Iniciar análisis/ }).click()
}
