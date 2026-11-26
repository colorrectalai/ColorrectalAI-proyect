// Elige el tono del borde de la ROI según la imagen que tiene debajo (CP-14, WCAG ≥ 3:1).
// Un solo color no contrasta con tejido claro y oscuro a la vez: se mide la luminancia de la
// franja de imagen que rodea el borde y se usa borde oscuro sobre fondo claro y claro sobre oscuro.
const cache = new Map()

// Luminancia relativa WCAG de un píxel sRGB (0–255).
function luminancia(r, g, b) {
  const lineal = (c) => {
    const v = c / 255
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * lineal(r) + 0.7152 * lineal(g) + 0.0722 * lineal(b)
}

function cargarImagen(url) {
  return new Promise((resolver, rechazar) => {
    const img = new Image()
    img.onload = () => resolver(img)
    img.onerror = rechazar
    img.src = url
  })
}

// Devuelve 'oscuro' si el fondo alrededor del borde es oscuro (usar borde claro) o 'claro'.
// Con luminancia ≈ 0.18 el negro y el blanco dan el mismo contraste: ese es el punto de corte.
export async function tonoFondoROI(url, roi) {
  const clave = `${url}|${roi.x}|${roi.y}|${roi.ancho}|${roi.alto}`
  if (cache.has(clave)) return cache.get(clave)
  let tono = 'claro'
  try {
    const img = await cargarImagen(url)
    const ancho = 256
    const alto = Math.max(1, Math.round((img.naturalHeight / img.naturalWidth) * ancho))
    const lienzo = document.createElement('canvas')
    lienzo.width = ancho
    lienzo.height = alto
    const ctx = lienzo.getContext('2d', { willReadFrequently: true })
    ctx.drawImage(img, 0, 0, ancho, alto)
    const px = ctx.getImageData(0, 0, ancho, alto).data

    const x0 = roi.x * ancho
    const y0 = roi.y * alto
    const x1 = (roi.x + roi.ancho) * ancho
    const y1 = (roi.y + roi.alto) * alto
    const banda = 4
    const valores = []
    for (let y = Math.max(0, Math.floor(y0 - banda)); y < Math.min(alto, Math.ceil(y1 + banda)); y++) {
      for (let x = Math.max(0, Math.floor(x0 - banda)); x < Math.min(ancho, Math.ceil(x1 + banda)); x++) {
        const cercaDelBorde = Math.min(Math.abs(x - x0), Math.abs(x - x1), Math.abs(y - y0), Math.abs(y - y1)) <= banda
        if (!cercaDelBorde) continue
        const i = (y * ancho + x) * 4
        valores.push(luminancia(px[i], px[i + 1], px[i + 2]))
      }
    }
    if (valores.length) {
      valores.sort((a, b) => a - b)
      tono = valores[Math.floor(valores.length / 2)] < 0.18 ? 'oscuro' : 'claro'
    }
  } catch {
    tono = 'claro'
  }
  cache.set(clave, tono)
  return tono
}
