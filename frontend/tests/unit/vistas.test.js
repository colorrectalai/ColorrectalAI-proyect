// Resultados, comparación (CF-04), menú, historial y aviso de uso experimental en cada pantalla.
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, montar, respuestaApi, router } from './ayuda'
import { estado } from '../../src/store'
import { guardarSesion } from '../../src/userProfile'

vi.mock('../../src/history', () => ({ guardarInterpretacion: vi.fn(), listarInterpretaciones: vi.fn(async () => []),
  restaurarInterpretacion: vi.fn(), obtenerInterpretacion: vi.fn(), obtenerMiniatura: vi.fn(async () => null), descargarResumen: vi.fn() }))
vi.mock('../../src/roiContraste', () => ({ tonoFondoROI: vi.fn(async () => 'oscuro') }))
vi.mock('../../src/reports/pdfReport', () => ({ descargarInformePdf: vi.fn() }))
const historial = await import('../../src/history')
const vista = async (n) => (await import(`../../src/views/${n}.vue`)).default
const resultado = (nombre, extra) => ({ nombre, url: 'blob:' + nombre, respuesta: respuestaApi({ id: nombre + 'x', ...extra }) })

beforeEach(() => {
  vi.clearAllMocks(); historial.listarInterpretaciones.mockResolvedValue([])
  estado.resultados = []; estado.fallidos = []; estado.id = ''
})

describe('ResultsView', () => {
  it('sin análisis muestra el estado vacío con enlace a cargar', async () => {
    const w = await montar(await vista('ResultsView'), '/resultados')
    expect(w.text()).toContain('Todavía no hay imágenes analizadas')
    expect(w.find('a[href="/carga"]').exists()).toBe(true)
  })
  it('lista las imágenes rechazadas con su mensaje (CF-02)', async () => {
    estado.resultados = [resultado('a.png')]; estado.fallidos = [{ nombre: 'mala.bmp', mensaje: 'Formato no admitido.' }]
    const w = await montar(await vista('ResultsView'), '/resultados')
    expect(w.find('.rejected-files').text()).toContain('mala.bmp')
    expect(w.find('.rejected-files').text()).toContain('Formato no admitido.')
  })
  it('dibuja una ROI por región detectada y usa borde claro sobre fondo oscuro', async () => {
    estado.resultados = [resultado('a.png', { rois: [{ x: 0.1, y: 0.1, ancho: 0.2, alto: 0.2, confianza: 0.8 },
      { x: 0.5, y: 0.5, ancho: 0.2, alto: 0.2, confianza: 0.7 }] })]
    const w = await montar(await vista('ResultsView'), '/resultados'); await flushPromises()
    const rois = w.findAll('.image-stage .roi-box')
    expect(rois).toHaveLength(2)
    expect(rois[0].classes()).toContain('sobre-fondo-oscuro')
  })
  it('navega entre imágenes', async () => {
    estado.resultados = [resultado('a.png'), resultado('b.png')]
    const w = await montar(await vista('ResultsView'), '/resultados')
    expect(w.text()).toContain('1 de 2 imágenes')
    await w.find('.next-button').trigger('click')
    expect(w.text()).toContain('2 de 2 imágenes')
  })
  it('muestra la máscara en blanco y negro cuando el modelo la entrega', async () => {
    estado.resultados = [resultado('a.png')]
    const w = await montar(await vista('ResultsView'), '/resultados')
    expect(w.find('img.mascara-bn').attributes('src')).toBe('data:image/png;base64,BBB')
  })
})

describe('CompareView (CF-04)', () => {
  it('muestra original, máscara y superposición por cada imagen', async () => {
    estado.id = 'A-1'; estado.resultados = [resultado('a.png'), resultado('b.png', { rois: [], mascara_bn: null, mascara_resultado: null })]
    const w = await montar(await vista('CompareView'), '/comparacion'); await flushPromises()
    const filas = w.findAll('.compare-row')
    expect(filas).toHaveLength(2)
    expect(filas[0].findAll('.stage')).toHaveLength(3)
    expect(filas[0].find('img.overlay').exists()).toBe(true)
    expect(filas[0].findAll('.roi')).toHaveLength(1)
  })
  it('los tres paneles comparten la proporción de la imagen (alineados)', async () => {
    estado.resultados = [resultado('a.png')]
    const w = await montar(await vista('CompareView'), '/comparacion')
    const estilos = w.findAll('.compare-row .stage').map((s) => s.attributes('style'))
    expect(new Set(estilos).size).toBe(1); expect(estilos[0]).toContain('800 / 600')
  })
  it('sin región indica que la máscara está vacía', async () => {
    estado.resultados = [resultado('b.png', { rois: [], mascara_bn: null, mascara_resultado: null })]
    const w = await montar(await vista('CompareView'), '/comparacion')
    expect(w.text()).toContain('Sin región: máscara vacía')
  })
  it('al entrar directo abre la interpretación más reciente del historial', async () => {
    historial.listarInterpretaciones.mockResolvedValue([{ id: 'A-9' }, { id: 'A-1' }])
    await montar(await vista('CompareView'), '/comparacion'); await flushPromises()
    expect(historial.restaurarInterpretacion).toHaveBeenCalledWith('A-9')
  })
  it('sin historial muestra cómo empezar', async () => {
    const w = await montar(await vista('CompareView'), '/comparacion'); await flushPromises()
    expect(w.text()).toContain('No hay una interpretación para comparar')
  })
})

describe('MainNav', () => {
  const nav = async () => (await import('../../src/components/MainNav.vue')).default
  it('sin sesión ofrece iniciar sesión y crear cuenta', async () => {
    const w = await montar(await nav(), '/')
    expect(w.text()).toContain('Iniciar sesión'); expect(w.text()).toContain('Crear cuenta')
  })
  it('con sesión muestra iniciales y nombre abreviado', async () => {
    guardarSesion({ token: 't', expira_en_s: 3600, usuario: { id: 1, nombre: 'Ana Ruiz', correo: 'a@x.co' } })
    const w = await montar(await nav(), '/inicio')
    expect(w.find('.avatar').text()).toBe('AR'); expect(w.find('.account-name').text()).toBe('Ana R.')
  })
  it('cerrar sesión borra el perfil y vuelve al inicio público', async () => {
    guardarSesion({ token: 't', expira_en_s: 3600, usuario: { id: 1, nombre: 'Ana Ruiz', correo: 'a@x.co' } })
    const w = await montar(await nav(), '/inicio')
    await w.find('button[aria-controls="profile-dropdown"]').trigger('click')
    expect(w.find('#profile-dropdown').text()).toContain('Ana Ruiz')
    await w.find('.logout-action').trigger('click'); await flushPromises()
    expect(localStorage.getItem('colorrectalai-token')).toBeNull()
    expect(router.currentRoute.value.path).toBe('/')
  })
  it('con el token vencido se comporta como sin sesión', async () => {
    guardarSesion({ token: 't', expira_en_s: -1, usuario: { id: 1, nombre: 'Ana', correo: 'a@x.co' } })
    const w = await montar(await nav(), '/inicio')
    expect(w.text()).toContain('Iniciar sesión')
  })
})

describe('Tabla e historial', () => {
  const item = (id, dias = 0) => ({ id, createdAt: new Date(Date.now() - dias * 864e5).toISOString(),
    resultados: [{ nombre: 'a.png', respuesta: respuestaApi() }] })
  it('tabla: estado de carga, vacío y filas', async () => {
    const Tabla = (await import('../../src/components/InterpretationHistoryTable.vue')).default
    let w = await montar(Tabla, '/', { props: { loading: true } }); expect(w.text()).toContain('Cargando historial')
    w = await montar(Tabla, '/', { props: { emptyTitle: 'Nada aún' } }); expect(w.text()).toContain('Nada aún')
    w = await montar(Tabla, '/', { props: { items: [item('A-1'), item('A-2')] } })
    expect(w.findAll('.open-button')).toHaveLength(2)
  })
  it('tabla: abrir y descargar emiten el elemento', async () => {
    const Tabla = (await import('../../src/components/InterpretationHistoryTable.vue')).default
    const w = await montar(Tabla, '/', { props: { items: [item('A-1')] } })
    await w.find('.open-button').trigger('click'); await w.find('.download-button').trigger('click')
    expect(w.emitted('open')[0][0].id).toBe('A-1'); expect(w.emitted('download')[0][0].id).toBe('A-1')
  })
  it('historial: pagina de a 5 y busca por ID', async () => {
    historial.listarInterpretaciones.mockResolvedValue(Array.from({ length: 7 }, (_, i) => item(`A-${i}`)))
    const w = await montar(await vista('HistoryView'), '/historial'); await flushPromises()
    expect(w.text()).toContain('Mostrando 1–5 de 7 interpretaciones')
    await w.find('input[type="search"]').setValue('A-6'); await flushPromises()
    expect(w.text()).toContain('Mostrando 1–1 de 1 interpretaciones')
  })
  it('historial: filtra por fecha', async () => {
    historial.listarInterpretaciones.mockResolvedValue([item('A-hoy'), item('A-vieja', 40)])
    const w = await montar(await vista('HistoryView'), '/historial'); await flushPromises()
    await w.find('select').setValue('30'); await flushPromises()
    expect(w.text()).toContain('de 1 interpretaciones')
  })
  it('historial: error al leer muestra el mensaje', async () => {
    historial.listarInterpretaciones.mockRejectedValue(new Error('Este navegador no permite guardar el historial local.'))
    const w = await montar(await vista('HistoryView'), '/historial'); await flushPromises()
    expect(w.text()).toContain('Este navegador no permite guardar el historial local.')
  })
})

describe('Aviso de uso experimental (RNF-016.1) en cada pantalla', () => {
  it.each([['HomeView', '/'], ['DashboardView', '/inicio'], ['UploadView', '/carga'], ['HistoryView', '/historial'],
    ['CompareView', '/comparacion']])('%s', async (nombre, ruta) => {
    const w = await montar(await vista(nombre), ruta); await flushPromises()
    expect(w.text()).toMatch(/diagn[oó]stico|profesional de salud|profesional de la salud/i)
  })
})
