// Historial local en IndexedDB: guardar, listar, abrir, restaurar y miniaturas.
import { beforeEach, describe, expect, it } from 'vitest'
import { IDBFactory } from 'fake-indexeddb'
let h, estado
beforeEach(async () => {
  globalThis.indexedDB = new IDBFactory()           // base nueva en cada prueba
  window.indexedDB = globalThis.indexedDB
  const { vi } = await import('vitest'); vi.resetModules()
  h = await import('../../src/history')
  estado = (await import('../../src/store')).estado
})

const archivo = (n) => new File([new Uint8Array([1, 2, 3, n])], `img${n}.png`, { type: 'image/png' })
const interp = (id, fecha, n = 1) => ({
  id, createdAt: fecha,
  resultados: Array.from({ length: n }, (_, i) => ({
    nombre: `img${i}.png`, archivo: archivo(i),
    respuesta: { clasificacion: 'posible_region', rois: [{ x: 0.1 }], imagen_resultado: 'data:pesado', modelo_version: 'seg-0.1' },
  })),
})

describe('history', () => {
  it('guarda y lista ordenado de la más reciente a la más antigua', async () => {
    await h.guardarInterpretacion(interp('A-1', '2026-11-20T10:00:00Z'))
    await h.guardarInterpretacion(interp('A-2', '2026-11-25T10:00:00Z'))
    expect((await h.listarInterpretaciones()).map((x) => x.id)).toEqual(['A-2', 'A-1'])
  })
  it('no guarda la imagen pesada con la ROI dibujada', async () => {
    await h.guardarInterpretacion(interp('A-1', '2026-11-20T10:00:00Z'))
    const [x] = await h.listarInterpretaciones()
    expect(x.resultados[0].respuesta.imagen_resultado).toBeUndefined()
    expect(x.resultados[0].respuesta.rois).toHaveLength(1)
  })
  it('obtenerInterpretacion devuelve cada resultado con su archivo', async () => {
    await h.guardarInterpretacion(interp('A-1', '2026-11-20T10:00:00Z', 3))
    const x = await h.obtenerInterpretacion('A-1')
    expect(x.resultados).toHaveLength(3)
    expect(x.resultados.every((r) => r.archivo)).toBe(true)
  })
  it('obtenerInterpretacion de un id inexistente devuelve null', async () => {
    expect(await h.obtenerInterpretacion('nada')).toBeNull()
  })
  it('restaurarInterpretacion carga el estado y limpia las rechazadas', async () => {
    estado.fallidos = [{ nombre: 'x', mensaje: 'y' }]
    await h.guardarInterpretacion(interp('A-9', '2026-11-20T10:00:00Z', 2))
    await h.restaurarInterpretacion('A-9')
    expect(estado.id).toBe('A-9'); expect(estado.resultados).toHaveLength(2)
    expect(estado.archivos).toHaveLength(2); expect(estado.fallidos).toEqual([])
  })
  it('restaurar una interpretación inexistente da un error claro', async () => {
    await expect(h.restaurarInterpretacion('nada')).rejects.toThrow(/No se encontró/)
  })
  it('obtenerMiniatura devuelve la primera imagen o null', async () => {
    await h.guardarInterpretacion(interp('A-1', '2026-11-20T10:00:00Z'))
    expect(await h.obtenerMiniatura('A-1')).toBeTruthy()
    expect(await h.obtenerMiniatura('nada')).toBeNull()
  })
})
