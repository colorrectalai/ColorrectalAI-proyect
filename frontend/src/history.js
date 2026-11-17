// Persistencia local del historial: conserva resultados y archivos en IndexedDB del navegador.
import { estado, liberarUrlsResultados } from './store'

const DATABASE_NAME = 'colorrectalai-history'
const DATABASE_VERSION = 1
const INTERPRETATIONS_STORE = 'interpretations'
const IMAGES_STORE = 'images'

let databasePromise

function openDatabase() {
  if (databasePromise) return databasePromise
  if (!('indexedDB' in window)) return Promise.reject(new Error('Este navegador no permite guardar el historial local.'))

  databasePromise = new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DATABASE_NAME, DATABASE_VERSION)
    request.onupgradeneeded = () => {
      const database = request.result
      if (!database.objectStoreNames.contains(INTERPRETATIONS_STORE)) {
        database.createObjectStore(INTERPRETATIONS_STORE, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(IMAGES_STORE)) {
        const images = database.createObjectStore(IMAGES_STORE, { keyPath: 'key' })
        images.createIndex('interpretationId', 'interpretationId', { unique: false })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error || new Error('No se pudo abrir el historial local.'))
    request.onblocked = () => reject(new Error('Cierra otras pestañas de ColorrectalAI para actualizar el historial.'))
  })

  return databasePromise
}

function requestResult(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error || new Error('No se pudo leer el historial local.'))
  })
}

function transactionResult(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve()
    transaction.onerror = () => reject(transaction.error || new Error('No se pudo guardar el historial local.'))
    transaction.onabort = () => reject(transaction.error || new Error('Se canceló el guardado del historial.'))
  })
}

// Guarda las respuestas de la API por separado de los archivos binarios.
export async function guardarInterpretacion(interpretacion) {
  const database = await openDatabase()
  const transaction = database.transaction([INTERPRETATIONS_STORE, IMAGES_STORE], 'readwrite')
  const completed = transactionResult(transaction)
  const interpretations = transaction.objectStore(INTERPRETATIONS_STORE)
  const images = transaction.objectStore(IMAGES_STORE)

  const resultados = interpretacion.resultados.map(({ nombre, respuesta }) => {
    // Las respuestas dentro del estado Vue son proxies y sus propiedades anidadas
    // también pueden serlo; JSON las convierte en objetos simples clonables.
    const respuestaPlana = JSON.parse(JSON.stringify(respuesta))
    delete respuestaPlana.imagen_resultado
    return { nombre, respuesta: respuestaPlana }
  })

  interpretations.put({
    id: interpretacion.id,
    createdAt: interpretacion.createdAt,
    resultados,
  })

  interpretacion.resultados.forEach(({ nombre, archivo }, index) => {
    if (!archivo) return
    const blob = archivo.slice(0, archivo.size, archivo.type)
    images.put({
      key: `${interpretacion.id}:${index}`,
      interpretationId: interpretacion.id,
      index,
      nombre,
      blob,
    })
  })

  await completed
}

// Devuelve solo los datos ligeros de cada análisis para construir la tabla.
export async function listarInterpretaciones() {
  const database = await openDatabase()
  const transaction = database.transaction(INTERPRETATIONS_STORE, 'readonly')
  const completed = transactionResult(transaction)
  const values = await requestResult(transaction.objectStore(INTERPRETATIONS_STORE).getAll())
  await completed
  return values.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
}

// Recupera el archivo original de una fila para mostrar su miniatura.
export async function obtenerMiniatura(id) {
  const database = await openDatabase()
  const transaction = database.transaction(IMAGES_STORE, 'readonly')
  const completed = transactionResult(transaction)
  const image = await requestResult(transaction.objectStore(IMAGES_STORE).get(`${id}:0`))
  await completed
  return image?.blob || null
}

// Recupera una interpretación completa para reabrirla en la vista de resultados.
export async function obtenerInterpretacion(id) {
  const database = await openDatabase()
  const transaction = database.transaction([INTERPRETATIONS_STORE, IMAGES_STORE], 'readonly')
  const completed = transactionResult(transaction)
  const interpretationRequest = transaction.objectStore(INTERPRETATIONS_STORE).get(id)
  const imagesRequest = transaction.objectStore(IMAGES_STORE).index('interpretationId').getAll(id)
  const [interpretacion, imagenes] = await Promise.all([
    requestResult(interpretationRequest),
    requestResult(imagesRequest),
  ])
  await completed
  if (!interpretacion) return null

  const porIndice = new Map(imagenes.map((imagen) => [imagen.index, imagen]))
  return {
    ...interpretacion,
    resultados: interpretacion.resultados.map((resultado, index) => ({
      ...resultado,
      archivo: porIndice.get(index)?.blob || null,
    })),
  }
}

// Restaura una interpretación guardada en el estado que consume ResultsView.
export async function restaurarInterpretacion(id) {
  const interpretacion = await obtenerInterpretacion(id)
  if (!interpretacion) throw new Error('No se encontró esta interpretación en el historial local.')

  const archivos = interpretacion.resultados.map((resultado) => {
    if (!resultado.archivo) {
      throw new Error('No se encontró una de las imágenes guardadas para esta interpretación.')
    }
    return new File([resultado.archivo], resultado.nombre, {
      type: resultado.archivo.type || 'image/jpeg',
    })
  })

  liberarUrlsResultados()
  estado.archivos = archivos
  estado.id = interpretacion.id
  estado.historialError = ''
  estado.resultados = interpretacion.resultados.map((resultado, index) => ({
    nombre: resultado.nombre,
    url: URL.createObjectURL(archivos[index]),
    respuesta: resultado.respuesta,
  }))

  return interpretacion
}

// Descarga los metadatos y resultados sin incluir las imágenes originales.
export function descargarResumen(interpretacion) {
  const contenido = {
    id: interpretacion.id,
    fecha: interpretacion.createdAt,
    resultados: interpretacion.resultados,
    aviso: 'Resultados experimentales con fines académicos. No constituyen un diagnóstico médico.',
  }
  const url = URL.createObjectURL(new Blob([JSON.stringify(contenido, null, 2)], { type: 'application/json' }))
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = `${interpretacion.id}-resumen.json`
  enlace.click()
  URL.revokeObjectURL(url)
}
