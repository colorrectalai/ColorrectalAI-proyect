// Perfil local de demostración, asociado al correo que se usa para iniciar sesión.
const PROFILES_KEY = 'colorrectalai-user-profiles'

function readProfiles() {
  try {
    const profiles = JSON.parse(localStorage.getItem(PROFILES_KEY) || '{}')
    return profiles && typeof profiles === 'object' && !Array.isArray(profiles) ? profiles : {}
  } catch {
    return {}
  }
}

function normalizeEmail(email) {
  return email.trim().toLocaleLowerCase('es-CO')
}

function nameFromEmail(email) {
  const localPart = normalizeEmail(email).split('@')[0] || 'usuario'
  return localPart
    .replace(/[._-]+/g, ' ')
    .trim()
    .split(/\s+/)
    .map((part) => part ? part[0].toLocaleUpperCase('es-CO') + part.slice(1) : '')
    .join(' ')
}

// Registra el nombre y activa el perfil en el navegador actual.
export function guardarPerfilLocal(email, nombre) {
  const correo = normalizeEmail(email)
  const nombreCompleto = nombre.trim()
  const perfiles = readProfiles()
  perfiles[correo] = nombreCompleto
  localStorage.setItem(PROFILES_KEY, JSON.stringify(perfiles))
  localStorage.setItem('colorrectalai-user-email', correo)
  localStorage.setItem('colorrectalai-user-name', nombreCompleto)
}

// Busca el nombre del registro o genera uno legible desde el correo en el prototipo.
export function activarPerfilLocal(email) {
  const correo = normalizeEmail(email)
  const nombre = readProfiles()[correo] || nameFromEmail(correo)
  localStorage.setItem('colorrectalai-user-email', correo)
  localStorage.setItem('colorrectalai-user-name', nombre)
}

// Al cerrar sesión conserva el directorio local, pero elimina el perfil activo.
export function limpiarPerfilActivo() {
  localStorage.removeItem('colorrectalai-user-email')
  localStorage.removeItem('colorrectalai-user-name')
  localStorage.removeItem('colorrectalai-session')
}
