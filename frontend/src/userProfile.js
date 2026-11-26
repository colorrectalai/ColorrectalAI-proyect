// Sesión del usuario en el navegador. La cuenta vive en el servidor (PostgreSQL, contraseña con hash);
// aquí solo se guardan el token de sesión, el correo y el nombre para el saludo. Nunca la contraseña.
const CLAVE_TOKEN = 'colorrectalai-token'
const CLAVE_VENCE = 'colorrectalai-token-vence'

// Guarda la sesión que devuelve la API al registrarse o iniciar sesión.
export function guardarSesion(sesion) {
  localStorage.setItem(CLAVE_TOKEN, sesion.token)
  localStorage.setItem(CLAVE_VENCE, String(Date.now() + sesion.expira_en_s * 1000))
  localStorage.setItem('colorrectalai-user-email', sesion.usuario.correo)
  localStorage.setItem('colorrectalai-user-name', sesion.usuario.nombre)
  localStorage.setItem('colorrectalai-session', 'active')
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
  if (tokenActual()) return true
  if (localStorage.getItem('colorrectalai-session')) limpiarPerfilActivo()
  return false
}

// Al cerrar sesión (o si el token venció) se borra todo el perfil activo.
export function limpiarPerfilActivo() {
  localStorage.removeItem(CLAVE_TOKEN)
  localStorage.removeItem(CLAVE_VENCE)
  localStorage.removeItem('colorrectalai-user-email')
  localStorage.removeItem('colorrectalai-user-name')
  localStorage.removeItem('colorrectalai-session')
}

// Borra el directorio de perfiles que guardaba la versión de demostración anterior.
localStorage.removeItem('colorrectalai-user-profiles')
