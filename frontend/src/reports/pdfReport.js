const PAGE_WIDTH = 210
const PAGE_HEIGHT = 297
const MARGIN = 15
const NAVY = [2, 23, 45]
const BLUE = [0, 157, 255]
const CYAN = [5, 197, 222]
const INK = [21, 50, 76]
const MUTED = [96, 124, 148]
const LINE = [220, 232, 241]

const porcentaje = (valor = 0) => `${(Number(valor || 0) * 100).toFixed(1)}%`
const numero = (valor = 0) => Number(valor || 0).toLocaleString('es-CO')
const clasificacion = (resultado) => resultado.respuesta.clasificacion === 'posible_region'
  ? 'Posible pólipo'
  : 'Sin hallazgos relevantes'

const fechaLocal = (valor) => {
  const fecha = new Date(valor)
  if (Number.isNaN(fecha.getTime())) return 'Fecha no disponible'
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(fecha)
}

const cargarImagen = (src) => new Promise((resolve, reject) => {
  const image = new Image()
  image.onload = () => resolve(image)
  image.onerror = () => reject(new Error('No se pudo preparar una imagen del informe.'))
  image.src = src
})

// Prepara la imagen final antes de insertarla en el PDF, incluyendo máscara y marcos ROI.
async function crearImagenInforme(resultado) {
  const { respuesta, archivo } = resultado
  if (!respuesta.imagen_resultado && !archivo) return ''
  const urlOriginal = archivo ? URL.createObjectURL(archivo) : ''

  try {
    const original = await cargarImagen(respuesta.imagen_resultado || urlOriginal)
    const escala = Math.min(1, 1600 / Math.max(original.naturalWidth, original.naturalHeight))
    const canvas = document.createElement('canvas')
    canvas.width = Math.max(1, Math.round(original.naturalWidth * escala))
    canvas.height = Math.max(1, Math.round(original.naturalHeight * escala))
    const context = canvas.getContext('2d')
    context.drawImage(original, 0, 0, canvas.width, canvas.height)

    const mascaraSrc = respuesta.mascara_resultado || respuesta.mascara_bn
    if (!respuesta.imagen_resultado && mascaraSrc) {
      const mascara = await cargarImagen(mascaraSrc)
      if (respuesta.mascara_resultado) {
        context.drawImage(mascara, 0, 0, canvas.width, canvas.height)
      } else {
        const maskCanvas = document.createElement('canvas')
        maskCanvas.width = canvas.width
        maskCanvas.height = canvas.height
        const maskContext = maskCanvas.getContext('2d', { willReadFrequently: true })
        maskContext.drawImage(mascara, 0, 0, canvas.width, canvas.height)
        const pixels = maskContext.getImageData(0, 0, canvas.width, canvas.height)
        for (let index = 0; index < pixels.data.length; index += 4) {
          const luminance = (pixels.data[index] + pixels.data[index + 1] + pixels.data[index + 2]) / 3
          pixels.data[index] = CYAN[0]
          pixels.data[index + 1] = CYAN[1]
          pixels.data[index + 2] = CYAN[2]
          pixels.data[index + 3] = luminance > 100 ? 170 : 0
        }
        maskContext.putImageData(pixels, 0, 0)
        context.drawImage(maskCanvas, 0, 0)
      }
    }

    if (respuesta.rois?.length) {
      const grosor = Math.max(2, canvas.width / 450)
      const fuente = Math.max(12, canvas.width / 60)
      context.lineWidth = grosor
      context.font = `700 ${fuente}px Arial`
      respuesta.rois.forEach((roi, index) => {
        const x = roi.x * canvas.width
        const y = roi.y * canvas.height
        const width = roi.ancho * canvas.width
        const height = roi.alto * canvas.height
        const etiqueta = `ROI ${String(index + 1).padStart(2, '0')}`
        const altoEtiqueta = fuente * 1.5
        context.strokeStyle = '#05c5de'
        context.strokeRect(x, y, width, height)
        context.fillStyle = '#05c5de'
        context.fillRect(x, Math.max(0, y - altoEtiqueta), context.measureText(etiqueta).width + 12, altoEtiqueta)
        context.fillStyle = '#02172d'
        context.fillText(etiqueta, x + 6, Math.max(fuente, y - fuente * 0.3))
      })
    }

    return canvas.toDataURL('image/jpeg', 0.92)
  } finally {
    if (urlOriginal) URL.revokeObjectURL(urlOriginal)
  }
}

async function cargarLogo() {
  try {
    const ruta = `${import.meta.env.BASE_URL}img/LogoColorrectalAI2.png`
    const response = await fetch(ruta)
    if (!response.ok) return ''
    const blob = await response.blob()
    return await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = () => reject(reader.error)
      reader.readAsDataURL(blob)
    })
  } catch {
    return ''
  }
}

function texto(doc, valor, x, y, opciones = {}) {
  const { color = INK, size = 9, bold = false, align, maxWidth } = opciones
  doc.setTextColor(...color)
  doc.setFont('helvetica', bold ? 'bold' : 'normal')
  doc.setFontSize(size)
  const lineas = maxWidth ? doc.splitTextToSize(String(valor ?? ''), maxWidth) : String(valor ?? '')
  doc.text(lineas, x, y, align ? { align } : undefined)
  return Array.isArray(lineas) ? lineas.length : 1
}

function rectangulo(doc, x, y, ancho, alto, color, borde = null, radio = 2) {
  doc.setFillColor(...color)
  if (borde) doc.setDrawColor(...borde)
  doc.roundedRect(x, y, ancho, alto, radio, radio, borde ? 'FD' : 'F')
}

function dibujarImagenContenida(doc, dataUrl, x, y, anchoMaximo, altoMaximo) {
  if (!dataUrl) return false
  try {
    const dimensiones = doc.getImageProperties(dataUrl)
    const escala = Math.min(anchoMaximo / dimensiones.width, altoMaximo / dimensiones.height)
    const ancho = dimensiones.width * escala
    const alto = dimensiones.height * escala
    doc.addImage(dataUrl, x + (anchoMaximo - ancho) / 2, y + (altoMaximo - alto) / 2, ancho, alto)
    return true
  } catch {
    return false
  }
}

function dibujarEncabezado(doc, interpretacion, logo) {
  doc.setFillColor(...NAVY)
  doc.rect(0, 0, PAGE_WIDTH, 39, 'F')
  if (logo) dibujarImagenContenida(doc, logo, MARGIN, 8, 48, 22)
  else texto(doc, 'ColorrectalAI', MARGIN, 20, { color: [255, 255, 255], size: 17, bold: true })

  const x = logo ? 70 : 78
  texto(doc, 'INFORME ACADÉMICO · RESULTADOS EXPERIMENTALES', x, 11, { color: [89, 204, 255], size: 7, bold: true })
  texto(doc, 'Resultados de interpretación', x, 21, { color: [255, 255, 255], size: 15, bold: true })
  texto(doc, `ID: ${interpretacion.id}`, x, 31, { color: [224, 239, 250], size: 9, bold: true })
}

function dibujarPie(doc) {
  const paginas = doc.internal.getNumberOfPages()
  for (let pagina = 1; pagina <= paginas; pagina++) {
    doc.setPage(pagina)
    doc.setDrawColor(...LINE)
    doc.line(MARGIN, 280, PAGE_WIDTH - MARGIN, 280)
    texto(doc, 'Resultados experimentales. No constituyen un diagnóstico ni reemplazan la evaluación de un profesional de la salud.', MARGIN, 286, { color: MUTED, size: 6.5, maxWidth: 155 })
    texto(doc, `${pagina} / ${paginas}`, PAGE_WIDTH - MARGIN, 286, { color: MUTED, size: 7, align: 'right' })
  }
}

function dibujarTarjetaResumen(doc, x, y, ancho, titulo, valor) {
  rectangulo(doc, x, y, ancho, 22, [245, 250, 254], LINE)
  texto(doc, titulo, x + 3, y + 7, { color: MUTED, size: 7, maxWidth: ancho - 6 })
  texto(doc, valor, x + 3, y + 17, { color: BLUE, size: 13, bold: true })
}

function dibujarCabeceraTabla(doc, y) {
  rectangulo(doc, MARGIN, y, PAGE_WIDTH - MARGIN * 2, 10, [234, 245, 253])
  texto(doc, 'IMAGEN', 18, y + 6.5, { color: NAVY, size: 7, bold: true })
  texto(doc, 'CLASIFICACIÓN', 51, y + 6.5, { color: NAVY, size: 7, bold: true })
  texto(doc, 'CONFIANZA', 104, y + 6.5, { color: NAVY, size: 7, bold: true })
  texto(doc, 'ROI', 139, y + 6.5, { color: NAVY, size: 7, bold: true })
  texto(doc, 'TIEMPO', 169, y + 6.5, { color: NAVY, size: 7, bold: true })
}

function dibujarTablaGeneral(doc, resultados, logo, interpretacion, indiceInicio = 0, yInicial = 121) {
  let y = yInicial
  dibujarCabeceraTabla(doc, y)
  y += 10

  for (let indice = indiceInicio; indice < resultados.length; indice++) {
    const resultado = resultados[indice]
    if (y + 25 > 273) {
      doc.addPage()
      dibujarEncabezado(doc, interpretacion, logo)
      texto(doc, 'Resumen de resultados · continuación', MARGIN, 51, { color: NAVY, size: 12, bold: true })
      y = 58
      dibujarCabeceraTabla(doc, y)
      y += 10
    }

    doc.setDrawColor(...LINE)
    doc.line(MARGIN, y + 24, PAGE_WIDTH - MARGIN, y + 24)
    dibujarImagenContenida(doc, resultado.imagenInforme, 17, y + 2, 28, 19)
    const nombreLineas = texto(doc, resultado.nombre, 49, y + 9, { color: NAVY, size: 8, bold: true, maxWidth: 49 })
    texto(doc, `Imagen ${String(indice + 1).padStart(2, '0')}`, 49, y + 17, { color: MUTED, size: 6.5 })
    texto(doc, clasificacion(resultado), 102, y + 10, { color: resultado.respuesta.rois?.length ? [4, 117, 86] : MUTED, size: 7, bold: true, maxWidth: 34 })
    texto(doc, porcentaje(resultado.respuesta.confianza), 139, y + 10, { color: NAVY, size: 8, bold: true })
    texto(doc, String(resultado.respuesta.rois?.length || 0), 146, y + 18, { color: MUTED, size: 6.5 })
    texto(doc, `${numero(resultado.respuesta.metricas?.latencia_ms)} ms`, 168, y + 11, { color: INK, size: 7 })
    y += Math.max(25, nombreLineas > 1 ? 27 : 25)
  }
  return y
}

function dibujarResumen(doc, interpretacion, resultados, logo) {
  dibujarEncabezado(doc, interpretacion, logo)
  texto(doc, `Generado: ${fechaLocal(new Date())}`, MARGIN, 48, { color: MUTED, size: 8 })
  texto(doc, `Interpretación: ${fechaLocal(interpretacion.createdAt)}`, MARGIN, 54, { color: MUTED, size: 8 })
  texto(doc, 'Vista general', MARGIN, 67, { color: BLUE, size: 8, bold: true })
  texto(doc, 'Resumen de resultados', MARGIN, 76, { color: NAVY, size: 15, bold: true })

  const regiones = resultados.reduce((total, resultado) => total + (resultado.respuesta.rois?.length || 0), 0)
  const conHallazgo = resultados.filter((resultado) => resultado.respuesta.rois?.length).length
  const confianzaMedia = resultados.length
    ? resultados.reduce((total, resultado) => total + Number(resultado.respuesta.confianza || 0), 0) / resultados.length
    : 0
  const tarjetaAncho = 42
  const gap = 4
  dibujarTarjetaResumen(doc, 15, 83, tarjetaAncho, 'Imágenes analizadas', String(resultados.length))
  dibujarTarjetaResumen(doc, 15 + tarjetaAncho + gap, 83, tarjetaAncho, 'Regiones de interés', String(regiones))
  dibujarTarjetaResumen(doc, 15 + (tarjetaAncho + gap) * 2, 83, tarjetaAncho, 'Imágenes con regiones', String(conHallazgo))
  dibujarTarjetaResumen(doc, 15 + (tarjetaAncho + gap) * 3, 83, tarjetaAncho, 'Confianza promedio', porcentaje(confianzaMedia))

  const modelo = resultados.find((resultado) => resultado.respuesta.modelo_version)?.respuesta.modelo_version || 'No especificado'
  texto(doc, `Modelo: ${modelo}`, MARGIN, 114, { color: MUTED, size: 8 })
  texto(doc, 'Resultados por imagen', MARGIN, 119, { color: NAVY, size: 10, bold: true })
  return dibujarTablaGeneral(doc, resultados, logo, interpretacion)
}

function dibujarPaginaIndividual(doc, resultado, indice, total, interpretacion, logo) {
  doc.addPage()
  dibujarEncabezado(doc, interpretacion, logo)
  texto(doc, `VISTA INDIVIDUAL · IMAGEN ${String(indice + 1).padStart(2, '0')} DE ${total}`, MARGIN, 49, { color: BLUE, size: 7, bold: true })
  const nombreLineas = texto(doc, resultado.nombre, MARGIN, 58, { color: NAVY, size: 13, bold: true, maxWidth: 140 })
  const clasificacionX = 154
  rectangulo(doc, clasificacionX, 44, 41, 11, resultado.respuesta.rois?.length ? [228, 248, 240] : [239, 244, 248])
  texto(doc, clasificacion(resultado), clasificacionX + 20.5, 51.5, { color: resultado.respuesta.rois?.length ? [4, 117, 86] : MUTED, size: 6.5, bold: true, align: 'center', maxWidth: 38 })

  const yImagen = 65 + Math.max(0, nombreLineas - 1) * 5
  doc.setDrawColor(...LINE)
  doc.roundedRect(MARGIN, yImagen, PAGE_WIDTH - MARGIN * 2, 106, 3, 3, 'S')
  if (!dibujarImagenContenida(doc, resultado.imagenInforme, MARGIN + 3, yImagen + 3, PAGE_WIDTH - MARGIN * 2 - 6, 100)) {
    texto(doc, 'Imagen original no disponible', PAGE_WIDTH / 2, yImagen + 55, { color: MUTED, size: 9, align: 'center' })
  }

  const metricas = resultado.respuesta.metricas || {}
  const datos = [
    ['Confianza del modelo', porcentaje(resultado.respuesta.confianza)],
    ['Regiones señaladas', String(resultado.respuesta.rois?.length || 0)],
    ['Procesamiento', `${numero(metricas.latencia_ms)} ms`],
    ['Versión del modelo', resultado.respuesta.modelo_version || 'No especificado'],
  ]
  const anchoTarjeta = 42
  const gap = 4
  const yTarjetas = yImagen + 112
  datos.forEach(([titulo, valor], index) => {
    const x = MARGIN + index * (anchoTarjeta + gap)
    rectangulo(doc, x, yTarjetas, anchoTarjeta, 22, [245, 250, 254], LINE)
    texto(doc, titulo, x + 2.5, yTarjetas + 7, { color: MUTED, size: 6, maxWidth: anchoTarjeta - 5 })
    texto(doc, valor, x + 2.5, yTarjetas + 16, { color: NAVY, size: 8, bold: true, maxWidth: anchoTarjeta - 5 })
  })

  let y = yTarjetas + 34
  texto(doc, 'Detalle de regiones de interés', MARGIN, y, { color: NAVY, size: 10, bold: true })
  y += 7
  const rois = resultado.respuesta.rois || []
  if (!rois.length) {
    texto(doc, 'El modelo no señaló regiones de interés en esta imagen.', MARGIN, y + 2, { color: MUTED, size: 8 })
    return
  }

  rois.forEach((roi, roiIndex) => {
    if (y + 13 > 273) {
      doc.addPage()
      dibujarEncabezado(doc, interpretacion, logo)
      texto(doc, `${resultado.nombre} · detalle de ROI`, MARGIN, 51, { color: NAVY, size: 11, bold: true })
      y = 60
    }
    doc.setDrawColor(...LINE)
    doc.line(MARGIN, y + 9, PAGE_WIDTH - MARGIN, y + 9)
    texto(doc, `ROI ${String(roiIndex + 1).padStart(2, '0')}`, MARGIN, y + 5, { color: NAVY, size: 8, bold: true })
    texto(doc, `Confianza ${porcentaje(roi.confianza)}`, 49, y + 5, { color: BLUE, size: 8, bold: true })
    texto(doc, `X ${porcentaje(roi.x)} · Y ${porcentaje(roi.y)} · ancho ${porcentaje(roi.ancho)} · alto ${porcentaje(roi.alto)}`, 91, y + 5, { color: MUTED, size: 6.5, maxWidth: 104 })
    y += 12
  })
}

export async function descargarInformePdf(interpretacion) {
  const { jsPDF } = await import('jspdf')
  const resultados = await Promise.all(interpretacion.resultados.map(async (resultado) => ({
    ...resultado,
    imagenInforme: await crearImagenInforme(resultado),
  })))
  const logo = await cargarLogo()
  const doc = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait', compress: true })

  dibujarResumen(doc, interpretacion, resultados, logo)
  resultados.forEach((resultado, indice) =>
    dibujarPaginaIndividual(doc, resultado, indice, resultados.length, interpretacion, logo),
  )
  dibujarPie(doc)
  doc.save(`${interpretacion.id}-resultados.pdf`)
}
