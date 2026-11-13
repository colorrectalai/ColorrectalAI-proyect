// Conexión con el backend de ColorrectalAI.
// En local usa http://localhost:8000. En producción define VITE_API_URL (URL de Render) en un archivo .env
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const MAX_BYTES = 7.5 * 1024 * 1024

// Si la imagen no es JPG/PNG (o pesa demasiado) se convierte en el navegador antes de enviarla.
async function prepararArchivo(archivo) {
  const esJpgPng = ['image/jpeg', 'image/png'].includes(archivo.type)
  if (esJpgPng && archivo.size <= MAX_BYTES) return archivo
  const bmp = await createImageBitmap(archivo)
  const f = Math.min(1, 2048 / Math.max(bmp.width, bmp.height))
  const lienzo = document.createElement('canvas')
  lienzo.width = Math.round(bmp.width * f)
  lienzo.height = Math.round(bmp.height * f)
  lienzo.getContext('2d').drawImage(bmp, 0, 0, lienzo.width, lienzo.height)
  return new Promise((ok) => lienzo.toBlob(ok, 'image/jpeg', 0.92))
}

// Envía una imagen a la API y devuelve la respuesta (ROI, clasificación, confianza...).
export async function analizarImagen(archivo) {
  let cuerpo
  try {
    cuerpo = await prepararArchivo(archivo)
  } catch {
    throw new Error('No se pudo leer la imagen "' + archivo.name + '".')
  }
  const datos = new FormData()
  datos.append('imagen', cuerpo, 'imagen')

  const control = new AbortController()
  const reloj = setTimeout(() => control.abort(), 90000) // el servicio gratuito puede tardar en despertar
  try {
    const resp = await fetch(BASE + '/api/v1/inferencias', { method: 'POST', body: datos, signal: control.signal })
    const json = await resp.json().catch(() => ({}))
    if (!resp.ok) throw new Error(json.error?.mensaje || 'El servidor respondió con un error (' + resp.status + ').')
    return json
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('El servidor tardó demasiado en responder. Intenta de nuevo.')
    if (e instanceof TypeError) throw new Error('No se pudo conectar con el servidor de análisis. ¿Está encendido el backend?')
    throw e
  } finally {
    clearTimeout(reloj)
  }
}
