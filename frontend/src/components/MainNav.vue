<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronDown, ChevronUp, CircleHelp, History, House, LogIn, LogOut, PanelsTopLeft, ScanSearch, UserRoundPlus } from '@lucide/vue'
import { haySesion, limpiarPerfilActivo } from '../userProfile'

const route = useRoute()
const router = useRouter()
// Solo muestra la navegación privada cuando hay una sesión con token vigente.
// La ruta es una dependencia reactiva para actualizarla al entrar o cerrar sesión.
const loggedInView = computed(() => {
  route.path
  return haySesion()
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
  <!-- Encabezado general; el logo vuelve al inicio apropiado para cada área. -->
  <header class="topbar" :class="{ 'is-scrolled': isScrolled }">
    <RouterLink class="brand" to="/" aria-label="ColorrectalAI, ir al inicio">
      <img src="/img/LogoColorrectalAI2.png" alt="ColorrectalAI" />
    </RouterLink>
    <!-- Navegación para las vistas internas de la aplicación. -->
    <nav v-if="loggedInView" aria-label="Navegación principal">
      <RouterLink to="/inicio" :class="{ active: route.path === '/inicio' }"><House :size="17" aria-hidden="true" /><span>Inicio</span></RouterLink>
      <RouterLink
        to="/carga"
        :class="{ active: ['/carga', '/analizando', '/resultados', '/comparacion'].some(path => route.path.startsWith(path)) }"
      ><ScanSearch :size="17" aria-hidden="true" /><span>Interpretación</span></RouterLink>
      <RouterLink to="/historial" :class="{ active: route.path.startsWith('/historial') }"><History :size="17" aria-hidden="true" /><span>Historial</span></RouterLink>
    </nav>
    <!-- Enlaces públicos para conocer el proyecto, acceder o crear una cuenta. -->
    <nav v-else aria-label="Navegación principal">
      <RouterLink to="/#acerca"><CircleHelp :size="17" aria-hidden="true" /><span>Acerca de</span></RouterLink>
      <RouterLink to="/acceso"><LogIn :size="17" aria-hidden="true" /><span>Iniciar sesión</span></RouterLink>
      <RouterLink class="button" to="/registro"><UserRoundPlus :size="17" aria-hidden="true" /><span>Crear cuenta</span></RouterLink>
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
</template>

<style scoped>
/* Fondo, altura y alineación del encabezado compartido. */
.topbar {
  position: sticky;
  top: 0;
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
  font-size:14px;
  text-decoration:none;
  padding:10px 12px;
  border-radius:15px;
  transition:background .15s ease,color .15s ease;
  white-space:nowrap;
}
.topbar nav a svg {
  flex:0 0 auto;
  color:var(--canvas);
}
.topbar nav a:not(.button):hover,
.topbar nav a.active:not(.button) {
  /* estilos de hover y activo para los enlaces normales */
  background:#12395b;
  color:#ffffff;
  text-decoration:none;
}

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
  .topbar nav {
    gap:2px;
  }
  .topbar nav a {
    padding:8px;
    font-size:12px;
  }
  .brand img {
    height:60px;
  }
}
@media(max-width:620px) {
  .topbar {
    display:grid;
    grid-template-columns:minmax(0, 1fr) auto;
    height:auto;
    min-height:64px;
    padding:0 14px;
    gap:2px 8px;
  }
  .brand {
    grid-column:1;
    grid-row:1;
  }
  .brand img {
    height:56px;
    max-width:220px;
  }
  .profile-menu {
    grid-column:2;
    grid-row:1;
  }
  .topbar nav {
    grid-column:1 / -1;
    grid-row:2;
    justify-content:space-between;
    overflow-x:auto;
    width:100%;
    margin:0;
    scrollbar-width:none;
  }
  .topbar nav::-webkit-scrollbar {
    display:none;
  }
  .topbar nav a {
    gap:5px;
    padding:8px 5px;
    font-size:10px;
  }
  .topbar nav a svg {
    width:14px;
    height:14px;
  }
  .account {
    padding:4px;
  }
  .profile-menu {
    margin-left:4px;
  }
  .account>span:not(.avatar) {
    display:none;
  }
}
@media (prefers-reduced-motion: reduce) {
  .topbar,
  .account,
  .profile-menu-enter-active,
  .profile-menu-leave-active {
    transition: none;
  }
}
</style>
