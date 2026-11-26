// Carga de imágenes y análisis (CF-02, RF-005.1): filtros, límite de 10, errores por imagen y aviso.
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { archivo, flushPromises, montar, respuestaApi, router } from './ayuda'
import { estado } from '../../src/store'

vi.mock('../../src/api', () => ({ analizarImagen: vi.fn(), iniciarSesion: vi.fn(), registrarUsuario: vi.fn(), usuarioActual: vi.fn() }))
vi.mock('../../src/history', () => ({ guardarInterpretacion: vi.fn(), listarInterpretaciones: vi.fn(async () => []),
  restaurarInterpretacion: vi.fn(), obtenerInterpretacion: vi.fn(), obtenerMiniatura: vi.fn(async () => null), descargarResumen: vi.fn() }))
const api = await import('../../src/api')
const historial = await import('../../src/history')
const { default: UploadView } = await import('../../src/views/UploadView.vue')
const { default: LoadingView } = await import('../../src/views/LoadingView.vue')

beforeEach(() => { vi.clearAllMocks(); estado.archivos = []; estado.resultados = []; estado.fallidos = [] })

async function elegir(w, archivos) {
  const input = w.find('input[type="file"]')
  Object.defineProperty(input.element, 'files', { value: archivos, configurable: true })
  await input.trigger('change')
}

describe('UploadView', () => {
  it('acepta JPG y PNG', async () => {
    const w = await montar(UploadView, '/carga')
    await elegir(w, [archivo('a.png'), archivo('b.jpg', 'image/jpeg')])
    expect(estado.archivos.map((f) => f.name)).toEqual(['a.png', 'b.jpg'])
  })
  it.each([['bmp', 'image/bmp'], ['gif', 'image/gif'], ['pdf', 'application/pdf'], ['webp', 'image/webp']])(
    'no agrega archivos %s', async (ext, tipo) => {
      const w = await montar(UploadView, '/carga'); await elegir(w, [archivo(`x.${ext}`, tipo)])
      expect(estado.archivos).toHaveLength(0)
    })
  it('no repite el mismo archivo', async () => {
    const w = await montar(UploadView, '/carga')
    await elegir(w, [archivo('a.png')]); await elegir(w, [archivo('a.png')])
    expect(estado.archivos).toHaveLength(1)
  })
  it('limita cada análisis a 10 imágenes', async () => {
    const w = await montar(UploadView, '/carga')
    await elegir(w, Array.from({ length: 12 }, (_, i) => archivo(`i${i}.png`, 'image/png', 10 + i)))
    expect(estado.archivos).toHaveLength(10)
  })
  it('el botón de analizar está desactivado sin imágenes', async () => {
    const w = await montar(UploadView, '/carga')
    expect(w.find('.analyze-button').attributes('disabled')).toBeDefined()
  })
  it('quitar elimina la imagen elegida', async () => {
    const w = await montar(UploadView, '/carga'); await elegir(w, [archivo('a.png'), archivo('b.png', 'image/png', 11)])
    await w.find('.remove-file').trigger('click')
    expect(estado.archivos.map((f) => f.name)).toEqual(['b.png'])
  })
  it('advierte que no se carguen datos de pacientes ni es diagnóstico', async () => {
    const w = await montar(UploadView, '/carga')
    expect(w.text()).toMatch(/No cargues datos identificables/); expect(w.text()).toMatch(/no brinda diagnósticos/)
  })
})

describe('LoadingView', () => {
  it('sin imágenes vuelve a /carga', async () => {
    await montar(LoadingView, '/analizando'); await flushPromises()
    expect(router.currentRoute.value.path).toBe('/carga')
  })
  it('analiza todas, guarda en el historial y abre los resultados', async () => {
    api.analizarImagen.mockResolvedValue(respuestaApi())
    estado.archivos = [archivo('a.png'), archivo('b.png', 'image/png', 11)]
    await montar(LoadingView, '/analizando'); await flushPromises()
    expect(api.analizarImagen).toHaveBeenCalledTimes(2)
    expect(estado.resultados).toHaveLength(2)
    expect(historial.guardarInterpretacion).toHaveBeenCalledTimes(1)
    expect(router.currentRoute.value.path).toBe('/resultados/A-ABC123')
  })
  it('CF-02: si la API rechaza una, las demás se analizan y se lista la rechazada', async () => {
    api.analizarImagen.mockResolvedValueOnce(respuestaApi()).mockRejectedValueOnce(new Error('Formato no admitido.'))
      .mockResolvedValueOnce(respuestaApi())
    estado.archivos = [archivo('a.png'), archivo('mala.png', 'image/png', 11), archivo('c.png', 'image/png', 12)]
    await montar(LoadingView, '/analizando'); await flushPromises()
    expect(estado.resultados.map((r) => r.nombre)).toEqual(['a.png', 'c.png'])
    expect(estado.fallidos).toEqual([{ nombre: 'mala.png', mensaje: 'Formato no admitido.' }])
    expect(estado.archivos.map((f) => f.name)).toEqual(['a.png', 'c.png'])
  })
  it('si todas fallan, muestra el error y no navega', async () => {
    api.analizarImagen.mockRejectedValue(new Error('El servidor tardó demasiado.'))
    estado.archivos = [archivo('a.png')]
    const w = await montar(LoadingView, '/analizando'); await flushPromises()
    expect(w.text()).toContain('El servidor tardó demasiado.')
    expect(w.text()).toContain('No se pudo completar el análisis')
    expect(router.currentRoute.value.path).toBe('/analizando')
  })
  it('si falla el historial local, igual muestra los resultados con un aviso', async () => {
    api.analizarImagen.mockResolvedValue(respuestaApi())
    historial.guardarInterpretacion.mockRejectedValue(new Error('Sin espacio'))
    estado.archivos = [archivo('a.png')]
    await montar(LoadingView, '/analizando'); await flushPromises()
    expect(estado.historialError).toBe('Sin espacio')
    expect(router.currentRoute.value.path).toMatch(/^\/resultados\//)
  })
  it('muestra el aviso de uso experimental mientras analiza', async () => {
    api.analizarImagen.mockReturnValue(new Promise(() => {}))
    estado.archivos = [archivo('a.png')]
    const w = await montar(LoadingView, '/analizando')
    expect(w.text()).toContain('no constituyen un diagnóstico médico')
  })
})
