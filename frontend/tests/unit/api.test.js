// Cliente de la API: éxito, errores de la API en español, red caída y tiempo de espera.
import { describe, expect, it, vi } from 'vitest'
import { analizarImagen, iniciarSesion, registrarUsuario, usuarioActual } from '../../src/api'

const respuesta = (status, cuerpo) => Promise.resolve({ ok: status < 400, status, json: () => Promise.resolve(cuerpo) })
const png = () => new File([new Uint8Array([137, 80, 78, 71])], 'a.png', { type: 'image/png' })

describe('analizarImagen', () => {
  it('envía la imagen por POST multipart y devuelve el JSON', async () => {
    const fetch = vi.fn(() => respuesta(200, { clasificacion: 'sin_hallazgos' }))
    vi.stubGlobal('fetch', fetch)
    expect(await analizarImagen(png())).toEqual({ clasificacion: 'sin_hallazgos' })
    const [url, opciones] = fetch.mock.calls[0]
    expect(url).toMatch(/\/api\/v1\/inferencias$/)
    expect(opciones.method).toBe('POST')
    expect(opciones.body.get('imagen')).toBeInstanceOf(Blob)
  })
  it('muestra el mensaje en español que envía la API', async () => {
    vi.stubGlobal('fetch', () => respuesta(415, { error: { codigo: 'FORMATO_NO_ADMITIDO', mensaje: 'Formato no admitido.' } }))
    await expect(analizarImagen(png())).rejects.toThrow('Formato no admitido.')
  })
  it('error sin cuerpo JSON: mensaje genérico con el código HTTP', async () => {
    vi.stubGlobal('fetch', () => Promise.resolve({ ok: false, status: 502, json: () => Promise.reject(new Error('x')) }))
    await expect(analizarImagen(png())).rejects.toThrow('(502)')
  })
  it('API apagada o sin red: mensaje claro', async () => {
    vi.stubGlobal('fetch', () => Promise.reject(new TypeError('Failed to fetch')))
    await expect(analizarImagen(png())).rejects.toThrow(/No se pudo conectar/)
  })
  it('API lenta: aborta y avisa al vencer el tiempo', async () => {
    vi.stubGlobal('fetch', () => Promise.reject(Object.assign(new Error('abort'), { name: 'AbortError' })))
    await expect(analizarImagen(png())).rejects.toThrow(/tardó demasiado/)
  })
  it('archivo ilegible para convertir: error en español', async () => {
    vi.stubGlobal('createImageBitmap', () => Promise.reject(new Error('no')))
    const bmp = new File([new Uint8Array(10)], 'foto.bmp', { type: 'image/bmp' })
    await expect(analizarImagen(bmp)).rejects.toThrow('No se pudo leer la imagen "foto.bmp".')
  })
})

describe('cuentas de usuario', () => {
  it('registrarUsuario envía los campos con el nombre que espera la API', async () => {
    const fetch = vi.fn(() => respuesta(201, { token: 't' })); vi.stubGlobal('fetch', fetch)
    await registrarUsuario({ nombre: 'Ana', correo: 'a@x.co', contrasena: 'ClaveSegura1', aceptaAviso: true })
    const [url, op] = fetch.mock.calls[0]
    expect(url).toMatch(/\/api\/v1\/usuarios$/)
    expect(JSON.parse(op.body)).toEqual({ nombre: 'Ana', correo: 'a@x.co', contrasena: 'ClaveSegura1', acepta_aviso: true })
    expect(op.headers['Content-Type']).toBe('application/json')
  })
  it('iniciarSesion hace POST a /sesiones', async () => {
    const fetch = vi.fn(() => respuesta(200, { token: 't' })); vi.stubGlobal('fetch', fetch)
    await iniciarSesion({ correo: 'a@x.co', contrasena: 'x' })
    expect(fetch.mock.calls[0][0]).toMatch(/\/api\/v1\/sesiones$/)
    expect(fetch.mock.calls[0][1].method).toBe('POST')
  })
  it('usuarioActual hace GET con el token Bearer y sin cuerpo', async () => {
    const fetch = vi.fn(() => respuesta(200, { id: 1 })); vi.stubGlobal('fetch', fetch)
    await usuarioActual('abc')
    const op = fetch.mock.calls[0][1]
    expect(op.method).toBe('GET'); expect(op.body).toBeUndefined()
    expect(op.headers.Authorization).toBe('Bearer abc')
  })
  it('el error conserva código y estado para la interfaz', async () => {
    vi.stubGlobal('fetch', () => respuesta(401, { error: { codigo: 'CREDENCIALES_INVALIDAS', mensaje: 'Correo o contraseña incorrectos.' } }))
    const e = await iniciarSesion({ correo: 'a', contrasena: 'b' }).catch((x) => x)
    expect(e.message).toBe('Correo o contraseña incorrectos.')
    expect(e.codigo).toBe('CREDENCIALES_INVALIDAS'); expect(e.estado).toBe(401)
  })
  it('sin red: mensaje de conexión', async () => {
    vi.stubGlobal('fetch', () => Promise.reject(new TypeError('net')))
    await expect(registrarUsuario({})).rejects.toThrow(/Revisa tu conexión/)
  })
  it('tiempo agotado: mensaje de espera', async () => {
    vi.stubGlobal('fetch', () => Promise.reject(Object.assign(new Error('a'), { name: 'AbortError' })))
    await expect(usuarioActual('t')).rejects.toThrow(/tardó demasiado/)
  })
})
