// Borde adaptativo de la ROI (CP-14): luminancia WCAG y elección del tono según el fondo.
import { describe, expect, it, vi } from 'vitest'
import { LUMINANCIA_CORTE, luminancia, tonoFondoROI, tonoPorLuminancia } from '../../src/roiContraste'

describe('luminancia WCAG', () => {
  it.each([[0, 0, 0, 0], [255, 255, 255, 1]])('rgb(%i,%i,%i) = %d', (r, g, b, l) => {
    expect(luminancia(r, g, b)).toBeCloseTo(l, 5)
  })
  it('el verde pesa más que el rojo y el azul', () => {
    expect(luminancia(0, 255, 0)).toBeGreaterThan(luminancia(255, 0, 0))
    expect(luminancia(255, 0, 0)).toBeGreaterThan(luminancia(0, 0, 255))
  })
  it('el punto de corte iguala el contraste con negro y con blanco', () => {
    const l = LUMINANCIA_CORTE
    expect((l + 0.05) / 0.05).toBeCloseTo(1.05 / (l + 0.05), 0)
  })
  it.each([[0.05, 'oscuro'], [0.17, 'oscuro'], [0.18, 'claro'], [0.6, 'claro']])('luminancia %d → fondo %s', (l, t) => {
    expect(tonoPorLuminancia(l)).toBe(t)
  })
})

function simularImagen(rgb) {
  vi.stubGlobal('Image', class { set src(_) { setTimeout(() => this.onload(), 0) } get naturalWidth() { return 100 } get naturalHeight() { return 100 } })
  const real = document.createElement.bind(document)
  vi.spyOn(document, 'createElement').mockImplementation((tag) => tag !== 'canvas' ? real(tag) : {
    width: 0, height: 0,
    getContext: () => ({
      drawImage() {},
      getImageData: (x, y, w, h) => ({ data: Uint8ClampedArray.from({ length: w * h * 4 }, (_, i) => (i % 4 === 3 ? 255 : rgb[i % 4])) }),
    }),
  })
}

describe('tonoFondoROI', () => {
  const roi = { x: 0.2, y: 0.2, ancho: 0.4, alto: 0.4 }
  it('fondo oscuro → "oscuro" (borde blanco)', async () => {
    simularImagen([20, 10, 10]); expect(await tonoFondoROI('blob:oscura', roi)).toBe('oscuro')
  })
  it('fondo claro → "claro" (borde oscuro)', async () => {
    simularImagen([230, 180, 170]); expect(await tonoFondoROI('blob:clara', roi)).toBe('claro')
  })
  it('si la imagen no carga, usa "claro" sin romper', async () => {
    vi.stubGlobal('Image', class { set src(_) { setTimeout(() => this.onerror(new Error('x')), 0) } })
    expect(await tonoFondoROI('blob:rota', roi)).toBe('claro')
  })
  it('guarda en caché el resultado de la misma imagen y ROI', async () => {
    simularImagen([20, 10, 10]); await tonoFondoROI('blob:cache', roi)
    simularImagen([250, 250, 250]); expect(await tonoFondoROI('blob:cache', roi)).toBe('oscuro')
  })
})
