// Formularios de acceso y registro (DEF-11): validaciones, llamada a la API, errores y sesión.
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, montar, router } from './ayuda'

vi.mock('../../src/api', () => ({ iniciarSesion: vi.fn(), registrarUsuario: vi.fn(), analizarImagen: vi.fn(), usuarioActual: vi.fn() }))
const api = await import('../../src/api')
const { default: LoginView } = await import('../../src/views/LoginView.vue')
const { default: RegisterView } = await import('../../src/views/RegisterView.vue')
const sesion = { token: 't.f', expira_en_s: 3600, usuario: { id: 1, nombre: 'Ana Ruiz', correo: 'ana@x.co', tipo_usuario: 'Estudiante' } }

beforeEach(() => { vi.clearAllMocks() })

describe('LoginView', () => {
  it('pide correo y contraseña antes de llamar a la API', async () => {
    const w = await montar(LoginView, '/acceso')
    await w.find('form').trigger('submit')
    expect(w.text()).toContain('Completa tu correo y contraseña')
    expect(api.iniciarSesion).not.toHaveBeenCalled()
  })
  it('con credenciales correctas guarda la sesión y va a /inicio', async () => {
    api.iniciarSesion.mockResolvedValue(sesion)
    const w = await montar(LoginView, '/acceso')
    await w.find('input[type="email"]').setValue('ana@x.co')
    await w.find('input[type="password"]').setValue('ClaveSegura1')
    await w.find('form').trigger('submit'); await flushPromises()
    expect(api.iniciarSesion).toHaveBeenCalledWith({ correo: 'ana@x.co', contrasena: 'ClaveSegura1' })
    expect(localStorage.getItem('colorrectalai-token')).toBe('t.f')
    expect(router.currentRoute.value.path).toBe('/inicio')
  })
  it('con clave incorrecta muestra el error y no entra', async () => {
    api.iniciarSesion.mockRejectedValue(new Error('Correo o contraseña incorrectos.'))
    const w = await montar(LoginView, '/acceso')
    await w.find('input[type="email"]').setValue('ana@x.co')
    await w.find('input[type="password"]').setValue('mala')
    await w.find('form').trigger('submit'); await flushPromises()
    expect(w.find('[role="alert"]').text()).toBe('Correo o contraseña incorrectos.')
    expect(localStorage.getItem('colorrectalai-session')).toBeNull()
    expect(router.currentRoute.value.path).toBe('/acceso')
  })
  it('desactiva el botón mientras verifica', async () => {
    let terminar; api.iniciarSesion.mockReturnValue(new Promise((r) => { terminar = r }))
    const w = await montar(LoginView, '/acceso')
    await w.find('input[type="email"]').setValue('a@x.co'); await w.find('input[type="password"]').setValue('x')
    await w.find('form').trigger('submit')
    expect(w.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(w.find('button[type="submit"]').text()).toContain('Verificando')
    terminar(sesion); await flushPromises()
  })
})

describe('RegisterView', () => {
  async function llenar(w, { nombre = 'Ana Ruiz', correo = 'ana@x.co', tipo = 'Estudiante', clave = 'ClaveSegura1', confirmar = clave, aviso = true } = {}) {
    await w.find('input[type="text"]').setValue(nombre)
    await w.find('input[type="email"]').setValue(correo)
    await w.find('select[name="userType"]').setValue(tipo)
    const claves = w.findAll('input[type="password"]')
    await claves[0].setValue(clave); await claves[1].setValue(confirmar)
    await w.find('input[type="checkbox"]').setValue(aviso)
    await w.find('form').trigger('submit'); await flushPromises()
  }
  it('campos vacíos', async () => {
    const w = await montar(RegisterView, '/registro'); await w.find('form').trigger('submit')
    expect(w.text()).toContain('Completa todos los campos')
  })
  it('sin tipo de usuario no llama a la API', async () => {
    const w = await montar(RegisterView, '/registro'); await llenar(w, { tipo: '' })
    expect(w.text()).toContain('Completa todos los campos'); expect(api.registrarUsuario).not.toHaveBeenCalled()
  })
  it('ofrece los tres tipos de usuario que acepta la API', async () => {
    const w = await montar(RegisterView, '/registro')
    const valores = w.findAll('select[name="userType"] option').map((o) => o.element.value).filter(Boolean)
    expect(valores).toEqual(['Estudiante', 'Profesional', 'Otro'])
  })
  it('el ojo muestra y oculta cada contraseña por separado', async () => {
    const w = await montar(RegisterView, '/registro')
    const botones = w.findAll('.password-visibility-toggle')
    await botones[0].trigger('click')
    expect(w.find('#register-password').attributes('type')).toBe('text')
    expect(w.find('#confirm-password').attributes('type')).toBe('password')
    expect(botones[0].attributes('aria-label')).toBe('Ocultar contraseña')
    await botones[0].trigger('click')
    expect(w.find('#register-password').attributes('type')).toBe('password')
  })
  it('contraseñas distintas', async () => {
    const w = await montar(RegisterView, '/registro'); await llenar(w, { confirmar: 'Otra12345' })
    expect(w.text()).toContain('Las contraseñas no coinciden'); expect(api.registrarUsuario).not.toHaveBeenCalled()
  })
  it('aviso legal sin aceptar', async () => {
    const w = await montar(RegisterView, '/registro'); await llenar(w, { aviso: false })
    expect(w.text()).toContain('Debes aceptar el aviso legal')
  })
  it('contraseña de menos de 8 caracteres', async () => {
    const w = await montar(RegisterView, '/registro'); await llenar(w, { clave: 'corta' })
    expect(w.text()).toContain('al menos 8 caracteres'); expect(api.registrarUsuario).not.toHaveBeenCalled()
  })
  it('registro correcto crea la sesión y va a /inicio', async () => {
    api.registrarUsuario.mockResolvedValue(sesion)
    const w = await montar(RegisterView, '/registro'); await llenar(w)
    expect(api.registrarUsuario).toHaveBeenCalledWith({ nombre: 'Ana Ruiz', correo: 'ana@x.co', tipoUsuario: 'Estudiante', contrasena: 'ClaveSegura1', aceptaAviso: true })
    expect(localStorage.getItem('colorrectalai-user-name')).toBe('Ana Ruiz')
    expect(localStorage.getItem('colorrectalai-user-type')).toBe('Estudiante')
    expect(router.currentRoute.value.path).toBe('/inicio')
  })
  it('correo ya registrado: muestra el mensaje de la API', async () => {
    api.registrarUsuario.mockRejectedValue(new Error('Ya existe una cuenta con ese correo. Inicie sesión.'))
    const w = await montar(RegisterView, '/registro'); await llenar(w)
    expect(w.text()).toContain('Ya existe una cuenta con ese correo')
    expect(router.currentRoute.value.path).toBe('/registro')
  })
})
