import { ref } from 'vue'

// La cuenta y su contraseña viven en el servidor; el navegador conserva solo el token y datos de presentación.
const CLAVE_TOKEN = 'colorrectalai-token'
const CLAVE_VENCE = 'colorrectalai-token-vence'
const CLAVE_SESION = 'colorrectalai-session'
const venceInicial = Number(localStorage.getItem(CLAVE_VENCE) || 0)

// Estado reactivo compartido para cambiar la navegación al iniciar o cerrar sesión.
export const sesionActiva = ref(Boolean(localStorage.getItem(CLAVE_TOKEN) && Date.now() < venceInicial))

// Guarda la sesión que devuelve la API al registrarse o iniciar sesión.
export function guardarSesion(sesion) {
  localStorage.setItem(CLAVE_TOKEN, sesion.token)
  localStorage.setItem(CLAVE_VENCE, String(Date.now() + sesion.expira_en_s * 1000))
  localStorage.setItem('colorrectalai-user-email', sesion.usuario.correo)
  localStorage.setItem('colorrectalai-user-name', sesion.usuario.nombre)
  if (sesion.usuario.tipo_usuario) localStorage.setItem('colorrectalai-user-type', sesion.usuario.tipo_usuario)
  localStorage.setItem(CLAVE_SESION, 'active')
  sesionActiva.value = true
}

// Token vigente o null si no hay sesión o ya venció.
export function tokenActual() {
  const token = localStorage.getItem(CLAVE_TOKEN)
  const vence = Number(localStorage.getItem(CLAVE_VENCE) || 0)
  if (!token || Date.now() >= vence) return null
  return token
}

// Hay sesión solo si el token sigue vigente; si venció, se limpia el perfil.
export function haySesion() {
  if (tokenActual()) {
    sesionActiva.value = true
    return true
  }
  if (localStorage.getItem(CLAVE_SESION)) limpiarPerfilActivo()
  sesionActiva.value = false
  return false
}

// Al cerrar sesión (o si el token venció) se borra todo el perfil activo.
export function limpiarPerfilActivo() {
  localStorage.removeItem(CLAVE_TOKEN)
  localStorage.removeItem(CLAVE_VENCE)
  localStorage.removeItem('colorrectalai-user-email')
  localStorage.removeItem('colorrectalai-user-name')
  localStorage.removeItem('colorrectalai-user-type')
  localStorage.removeItem(CLAVE_SESION)
  sesionActiva.value = false
}
