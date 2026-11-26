// Estado compartido, rutas y datos del flujo de trabajo.
import { describe, expect, it } from 'vitest'
import { estado, liberarUrlsResultados } from '../../src/store'
import router from '../../src/router'
import { workflowSteps } from '../../src/data/workflowSteps'

describe('store', () => {
  it('estado inicial vacío', () => {
    expect(estado.archivos).toEqual([]); expect(estado.fallidos).toEqual([]); expect(estado.id).toBe('')
  })
  it('libera solo las URL blob al reemplazar resultados', () => {
    URL.revokeObjectURL.mockClear()
    estado.resultados = [{ url: 'blob:1' }, { url: 'data:image/png;base64,x' }, { url: 'blob:2' }]
    liberarUrlsResultados()
    expect(URL.revokeObjectURL.mock.calls.map((c) => c[0])).toEqual(['blob:1', 'blob:2'])
    estado.resultados = []
  })
})

describe('router', () => {
  const rutas = [['/', 'public-home'], ['/inicio', 'dashboard'], ['/acceso', 'login'], ['/registro', 'register'],
    ['/carga', 'upload'], ['/analizando', 'loading'], ['/resultados', 'results'], ['/resultados/A-1', 'results'],
    ['/comparacion', 'comparison'], ['/historial', 'history'], ['/historial/A-1', 'history-detail']]
  it.each(rutas)('%s abre la vista %s', (ruta, nombre) => {
    expect(router.resolve(ruta).name).toBe(nombre)
  })
  it('las rutas con parámetro reciben el id', () => {
    expect(router.resolve('/resultados/A-123').params.id).toBe('A-123')
  })
  it('una ruta desconocida no resuelve a ninguna vista', () => {
    expect(router.resolve('/no-existe').matched).toHaveLength(0)
  })
})

describe('pasos del flujo', () => {
  it('son 4 pasos numerados 01 a 04', () => {
    expect(workflowSteps.map((p) => p.number)).toEqual(['01', '02', '03', '04'])
  })
  it('cada paso tiene título, descripción e ícono', () => {
    for (const p of workflowSteps) { expect(p.title).toBeTruthy(); expect(p.description).toBeTruthy(); expect(p.icon).toBeTruthy() }
  })
})
