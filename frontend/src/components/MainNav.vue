<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRightFromLine, ChevronDown, ChevronUp, CircleHelp, History, House, Info, LogIn, LogOut, ScanSearch, UserRoundPlus } from '@lucide/vue'
import { haySesion, limpiarPerfilActivo, sesionActiva } from '../userProfile'

const route = useRoute()
const router = useRouter()
// La ruta vuelve a validar el token y el estado reactivo permite cerrar la sesión al instante.
const loggedInView = computed(() => {
  route.path
  return sesionActiva.value && haySesion()
})
// Nombre guardado durante el registro; la ruta reactiva actualiza el dato al iniciar sesión.
const accountName = computed(() => {
  route.path
  return localStorage.getItem('colorrectalai-user-name')?.trim() || 'Usuario'
})
const accountLabel = computed(() => {
  const [firstName, surname] = accountName.value.split(/\s+/).filter(Boolean)
  return surname ? `${firstName} ${[...surname][0].toLocaleUpperCase('es-CO')}.` : firstName
})
const accountInitials = computed(() => {
  const [firstName, surname] = accountName.value.split(/\s+/).filter(Boolean)
  return `${firstName?.[0] || ''}${surname ? [...surname][0] : ''}`.toLocaleUpperCase('es-CO')
})
const profileMenuOpen = ref(false)
const profileMenu = ref(null)
const navigationOpen = ref(false)

function closeProfileMenuOnOutsideClick(event) {
  if (!profileMenu.value?.contains(event.target)) profileMenuOpen.value = false
}

function logout() {
  profileMenuOpen.value = false
  limpiarPerfilActivo()
  router.push('/')
}

const isScrolled = ref(false)
const updateScrollState = () => {
  isScrolled.value = window.scrollY > 8
}

onMounted(() => {
  updateScrollState()
  window.addEventListener('scroll', updateScrollState, { passive: true })
  document.addEventListener('pointerdown', closeProfileMenuOnOutsideClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollState)
  document.removeEventListener('pointerdown', closeProfileMenuOnOutsideClick)
})
</script>
<template>
  <div class="navigation-shell" @keydown.esc.window="navigationOpen = false; profileMenuOpen = false">
    <!-- Encabezado fijo en flujo para mostrar la marca y el perfil. -->
    <header class="topbar" :class="{ 'is-scrolled': isScrolled }">
      <RouterLink class="brand" to="/" aria-label="ColorrectalAI, ir al inicio">
        <img src="/img/LogoColorrectalAI2.png" alt="ColorrectalAI" />
      </RouterLink>
      <!-- En escritorio se conserva la navegación horizontal original. -->
      <nav v-if="loggedInView" aria-label="Navegación principal">
        <RouterLink to="/inicio" :class="{ active: route.path === '/inicio' }"><House :size="18" aria-hidden="true" /><span>Inicio</span></RouterLink>
        <RouterLink to="/carga" :class="{ active: ['/carga', '/analizando', '/resultados', '/comparacion'].some(path => route.path.startsWith(path)) }"><ScanSearch :size="18" aria-hidden="true" /><span>Interpretación</span></RouterLink>
        <RouterLink to="/historial" :class="{ active: route.path.startsWith('/historial') }"><History :size="18" aria-hidden="true" /><span>Historial</span></RouterLink>
      </nav>
      <nav v-else aria-label="Navegación principal">
        <RouterLink to="/#acerca"><CircleHelp :size="18" aria-hidden="true" /><span>Acerca de</span></RouterLink>
        <RouterLink to="/acceso"><LogIn :size="18" aria-hidden="true" /><span>Iniciar sesión</span></RouterLink>
        <RouterLink class="button" to="/registro"><UserRoundPlus :size="18" aria-hidden="true" /><span>Crear cuenta</span></RouterLink>
      </nav>
      <!-- Perfil desplegable con opción para cerrar la sesión de demostración. -->
      <div v-if="loggedInView" ref="profileMenu" class="profile-menu" @keydown.esc.stop="profileMenuOpen = false">
        <button
          class="account"
          type="button"
          aria-controls="profile-dropdown"
          :aria-expanded="profileMenuOpen"
          aria-haspopup="true"
          @click="profileMenuOpen = !profileMenuOpen"
        >
          <span class="avatar">{{ accountInitials }}</span>
          <span class="account-name">{{ accountLabel }}</span>
          <ChevronUp v-if="profileMenuOpen" class="account-chevron" :size="16" :stroke-width="2" aria-hidden="true" />
          <ChevronDown v-else class="account-chevron" :size="16" :stroke-width="2" aria-hidden="true" />
        </button>
        <Transition name="profile-menu">
          <div v-if="profileMenuOpen" id="profile-dropdown" class="profile-dropdown">
            <div class="profile-identity">
              <span class="profile-menu-label">Sesión iniciada como</span>
              <strong>{{ accountName }}</strong>
            </div>
            <button class="logout-action" type="button" @click="logout">
              <LogOut :size="17" :stroke-width="1.8" aria-hidden="true" />
              Cerrar sesión
            </button>
          </div>
        </Transition>
      </div>
    </header>

    <!-- Pestaña fija a mitad del borde izquierdo que abre el menú lateral. -->
    <button
      class="nav-drawer-toggle"
      type="button"
      aria-controls="primary-navigation"
      :aria-expanded="navigationOpen"
      :aria-label="navigationOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'"
      @click="navigationOpen = !navigationOpen"
    >
      <ArrowRightFromLine class="nav-drawer-icon" :size="17" aria-hidden="true" />
      <span>Menú</span>
    </button>

    <!-- Fondo superpuesto y panel vertical de navegación. -->
    <Transition name="navigation-drawer">
      <div v-if="navigationOpen" class="drawer-backdrop" @click.self="navigationOpen = false">
        <nav id="primary-navigation" class="drawer-panel" aria-label="Navegación principal">
          <div class="drawer-heading">
            <img src="/img/Logotipo.png" alt="" aria-hidden="true" />
            <span>ColorrectalAI</span>
          </div>

          <div v-if="loggedInView" class="drawer-links">
            <RouterLink to="/" :class="{ active: route.path === '/' }" @click="navigationOpen = false"><Info :size="20" aria-hidden="true" /><span>ColorrectalAI</span></RouterLink>
            <RouterLink to="/inicio" :class="{ active: route.path === '/inicio' }" @click="navigationOpen = false"><House :size="20" aria-hidden="true" /><span>Inicio</span></RouterLink>
            <RouterLink to="/carga" :class="{ active: ['/carga', '/analizando', '/resultados', '/comparacion'].some(path => route.path.startsWith(path)) }" @click="navigationOpen = false"><ScanSearch :size="20" aria-hidden="true" /><span>Interpretación</span></RouterLink>
            <RouterLink to="/historial" :class="{ active: route.path.startsWith('/historial') }" @click="navigationOpen = false"><History :size="20" aria-hidden="true" /><span>Historial</span></RouterLink>
          </div>

          <div v-else class="drawer-links">
            <RouterLink to="/#acerca" @click="navigationOpen = false"><Info :size="20" aria-hidden="true" /><span>Acerca de</span></RouterLink>
            <RouterLink to="/acceso" @click="navigationOpen = false"><LogIn :size="20" aria-hidden="true" /><span>Iniciar sesión</span></RouterLink>
            <RouterLink to="/registro" @click="navigationOpen = false"><UserRoundPlus :size="20" aria-hidden="true" /><span>Crear cuenta</span></RouterLink>
          </div>
        </nav>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Fondo, altura y alineación del encabezado compartido. */
.navigation-shell {
  position: sticky;
  top: 0;
  z-index: 1000;
}
.topbar {
  position: relative;
  z-index: 1000;
  width: 100%;
  box-sizing: border-box;
  height:80px;
  transition: background-color .2s ease, box-shadow .2s ease;
  background:var(--navy);
  display:flex;
  align-items:center;
  padding:0 max(calc((100vw - 1280px)/2),5vw);
  color:#fff;
  gap:28px;
}
.topbar.is-scrolled {
  background: rgba(2, 23, 45, .96);
  box-shadow: 0 8px 24px rgba(0, 12, 27, .2);
  backdrop-filter: blur(10px);
}
.brand {
  display:flex;
  align-items:center;
  color:#fff;
  text-decoration:none;
  white-space:nowrap;
}
.brand img {
  display:block;
  width:auto;
  width:auto;
  height:80px;
  object-fit:contain;
  object-position:left center;
}
.topbar nav {
  margin-left:auto;
  display:flex;
  align-items:center;
  gap:8px;
}
.topbar nav a {
  display:inline-flex;
  align-items:center;
  gap:7px;
  color:var(--canvas);
  font-size:15px;
  text-decoration:none;
  padding:11px 13px;
  border-radius:15px;
  transition:background .15s ease,color .15s ease;
  white-space:nowrap;
}
.topbar nav a svg { flex:0 0 auto; color:var(--canvas); }
.topbar nav a:not(.button):hover,
.topbar nav a.active:not(.button) {
  background:#12395b;
  color:#ffffff;
}
.nav-drawer-toggle {
  position:fixed;
  top:50%;
  left:0;
  z-index:1303;
  display:none;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:4px;
  width:44px;
  height:78px;
  padding:8px 4px;
  border:1px solid rgb(255 255 255 / 28%);
  border-left:0;
  border-radius:0 14px 14px 0;
  background:var(--navy);
  color:#fff;
  font-size:10px;
  font-weight:500;
  line-height:1;
  box-shadow:0 6px 20px rgb(2 23 45 / 24%);
  cursor:pointer;
  transform:translateY(-50%);
  transition:left .24s ease, transform .24s ease, background-color .16s ease;
}
.nav-drawer-toggle:hover { background:#07345a; }
.nav-drawer-toggle[aria-expanded='true'] {
  left:min(280px, 72vw);
  border-left:1px solid rgb(255 255 255 / 28%);
  border-right:0;
  border-radius:14px 0 0 14px;
  transform:translateY(-50%);
}
.nav-drawer-toggle[aria-expanded='true'] .nav-drawer-icon { transform:rotate(180deg); }
.nav-drawer-icon { transition:transform .2s ease; }
.drawer-backdrop {
  position:fixed;
  inset:0;
  z-index:1301;
  background:rgb(2 15 29 / 58%);
  backdrop-filter:blur(3px);
}
.drawer-panel {
  position:absolute;
  inset:0 auto 0 0;
  display:flex;
  width:min(280px, 72vw);
  flex-direction:column;
  gap:34px;
  padding:34px 20px;
  border-right:1px solid rgb(255 255 255 / 12%);
  background:linear-gradient(160deg, #08223b 0%, var(--navy) 72%);
  box-shadow:16px 0 44px rgb(0 0 0 / 22%);
}
.drawer-heading {
  display:flex;
  align-items:center;
  gap:12px;
  min-height:54px;
  padding:0 8px 20px;
  border-bottom:1px solid rgb(255 255 255 / 14%);
  color:#fff;
  font-size:18px;
  font-weight:700;
}
.drawer-heading img { width:42px; height:42px; object-fit:contain; }
.drawer-links { display:flex; flex-direction:column; gap:8px; }
.drawer-links a {
  display:flex;
  align-items:center;
  gap:14px;
  min-height:58px;
  padding:0 16px;
  border:1px solid transparent;
  border-radius:12px;
  color:#e8f4ff;
  font-size:16px;
  font-weight:500;
  text-decoration:none;
  transition:background-color .16s ease, border-color .16s ease, color .16s ease;
}
.drawer-links a:hover,
.drawer-links a.active {
  border-color:rgb(0 157 255 / 32%);
  background:rgb(0 157 255 / 16%);
  color:#fff;
}
.drawer-links a svg { flex:0 0 auto; color:#45c4ff; }
.navigation-drawer-enter-active,
.navigation-drawer-leave-active { transition:opacity .22s ease; }
.navigation-drawer-enter-active .drawer-panel,
.navigation-drawer-leave-active .drawer-panel { transition:transform .24s cubic-bezier(.2,.7,.2,1); }
.navigation-drawer-enter-from,
.navigation-drawer-leave-to { opacity:0; }
.navigation-drawer-enter-from .drawer-panel,
.navigation-drawer-leave-to .drawer-panel { transform:translateX(-100%); }

.account {
  display:flex;
  align-items:center;
  gap:10px;
  padding:5px 7px;
  border:0;
  border-radius:12px;
  background:transparent;
  color:white;
  font-size:12px;
  cursor:pointer;
  transition:background-color .16s ease;
}
.account-name {
  white-space:nowrap;
}
.account:hover,
.account[aria-expanded='true'] {
  background:rgba(255, 255, 255, .1);
}
.profile-menu {
  position:relative;
  margin-left:10px;
}
.profile-dropdown {
  position:absolute;
  top:calc(100% + 12px);
  right:0;
  z-index:1200;
  width:min(250px, calc(100vw - 28px));
  padding:8px;
  border:1px solid var(--line);
  border-radius:14px;
  background:var(--surface);
  box-shadow:0 16px 38px rgba(1, 20, 38, .22);
  color:var(--navy);
  transform-origin:top right;
}
.profile-identity {
  display:flex;
  flex-direction:column;
  gap:4px;
  padding:10px 11px 13px;
  border-bottom:1px solid var(--line);
}
.profile-menu-label {
  color:var(--muted);
  font-size:11px;
}
.profile-identity strong {
  overflow:hidden;
  color:var(--navy);
  font-size:14px;
  font-weight:600;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.logout-action {
  display:flex;
  align-items:center;
  gap:10px;
  width:100%;
  margin-top:6px;
  padding:10px 11px;
  border:0;
  border-radius:9px;
  background:transparent;
  color:#b42332;
  font-size:13px;
  font-weight:600;
  text-align:left;
  cursor:pointer;
  transition:background-color .15s ease;
}
.logout-action:hover {
  background:#fff0f1;
}
.profile-menu-enter-active,
.profile-menu-leave-active {
  transition:opacity .16s ease, transform .16s ease;
}
.profile-menu-enter-from,
.profile-menu-leave-to {
  opacity:0;
  transform:translateY(-5px) scale(.98);
}
.avatar {
  width:32px;
  height:32px;
  display:grid;
  place-items:center;
  border-radius:50%;
  background:#e4f1f5;
  color:#155777;
  font-size:11px;
  font-weight:700;
}
.account-chevron {
  color:#a9bdcc;
}
/* Ajustes para que los enlaces sigan cabiendo en tablet y móvil. */
@media(max-width:850px) {
  .topbar {
    padding:0 22px;
    gap:10px;
  }
  .brand img {
    height:60px;
  }
  .topbar nav { display:none; }
  .nav-drawer-toggle { display:flex; }
}
@media(max-width:620px) {
  .topbar {
    display:flex;
    height:64px;
    padding:0 14px;
    gap:8px;
    justify-content:space-between;
  }
  .brand img {
    height:56px;
    max-width:220px;
  }
  .brand { min-width:0; }
  .account {
    min-height:44px;
    padding:4px;
  }
  .profile-menu {
    margin-left:4px;
  }
  .account>span:not(.avatar) {
    display:none;
  }
  .drawer-panel { width:min(250px, 72vw); padding:26px 14px; }
  .nav-drawer-toggle[aria-expanded='true'] { left:min(250px, 72vw); }
}
@media (min-width:851px) {
  .drawer-backdrop { display:none !important; }
}
@media (prefers-reduced-motion: reduce) {
  .topbar,
  .nav-drawer-toggle,
  .navigation-drawer-enter-active,
  .navigation-drawer-leave-active,
  .navigation-drawer-enter-active .drawer-panel,
  .navigation-drawer-leave-active .drawer-panel,
  .account,
  .profile-menu-enter-active,
  .profile-menu-leave-active {
    transition: none;
  }
}
</style>
