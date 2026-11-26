// Sesión del usuario en el navegador (DEF-11, RNF-015.1): token, vencimiento y limpieza.
import { describe, expect, it } from 'vitest'
import { guardarSesion, haySesion, limpiarPerfilActivo, tokenActual } from '../../src/userProfile'

const sesion = (segundos = 3600) => ({
  token: 'carga.firma', expira_en_s: segundos,
  usuario: { id: 1, nombre: 'Ana María', correo: 'ana@ejemplo.co' },
})

describe('userProfile', () => {
  it('guarda token, correo y nombre de la sesión', () => {
    guardarSesion(sesion())
    expect(localStorage.getItem('colorrectalai-token')).toBe('carga.firma')
    expect(localStorage.getItem('colorrectalai-user-email')).toBe('ana@ejemplo.co')
    expect(localStorage.getItem('colorrectalai-user-name')).toBe('Ana María')
    expect(localStorage.getItem('colorrectalai-session')).toBe('active')
  })
  it('nunca guarda una contraseña en el navegador', () => {
    guardarSesion(sesion())
    expect(JSON.stringify({ ...localStorage })).not.toMatch(/contrase|password|clave/i)
  })
  it('tokenActual devuelve el token vigente', () => {
    guardarSesion(sesion()); expect(tokenActual()).toBe('carga.firma')
  })
  it('tokenActual devuelve null con el token vencido', () => {
    guardarSesion(sesion(-1)); expect(tokenActual()).toBeNull()
  })
  it('tokenActual devuelve null sin sesión', () => { expect(tokenActual()).toBeNull() })
  it('haySesion es verdadero con token vigente', () => { guardarSesion(sesion()); expect(haySesion()).toBe(true) })
  it('haySesion limpia el perfil si el token venció', () => {
    guardarSesion(sesion(-1))
    expect(haySesion()).toBe(false)
    expect(localStorage.getItem('colorrectalai-user-name')).toBeNull()
  })
  it('limpiarPerfilActivo borra todos los datos de la sesión', () => {
    guardarSesion(sesion()); limpiarPerfilActivo()
    for (const k of ['colorrectalai-token', 'colorrectalai-token-vence', 'colorrectalai-user-email',
      'colorrectalai-user-name', 'colorrectalai-session']) expect(localStorage.getItem(k)).toBeNull()
  })
})
