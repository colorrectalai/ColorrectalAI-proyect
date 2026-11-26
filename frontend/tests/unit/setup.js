// Preparación común de las pruebas unitarias (Vitest + jsdom).
import 'fake-indexeddb/auto'
import { afterEach, beforeEach, vi } from 'vitest'

// jsdom no implementa estas APIs del navegador; se simulan.
URL.createObjectURL = vi.fn(() => 'blob:prueba')
URL.revokeObjectURL = vi.fn()
window.scrollTo = vi.fn()
window.matchMedia = vi.fn((q) => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {},
  addListener() {}, removeListener() {} }))

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})
