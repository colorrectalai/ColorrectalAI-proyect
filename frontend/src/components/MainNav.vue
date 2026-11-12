<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BrandLogo from './BrandLogo.vue'

const route = useRoute()
// Detecta si la ruta pertenece al área de trabajo que ve un usuario con sesión.
const loggedInView = computed(() => ['/inicio','/historial','/carga','/resultados','/comparacion'].some(path => route.path.startsWith(path)))
</script>
<template>
  <!-- Encabezado general; el logo vuelve al inicio apropiado para cada área. -->
  <header class="topbar">
    <RouterLink class="brand" :to="loggedInView ? '/inicio' : '/'"><BrandLogo compact /></RouterLink>
    <!-- Navegación para las vistas internas de la aplicación. -->
    <nav v-if="loggedInView" aria-label="Navegación principal">
      <RouterLink to="/inicio" :class="{ active: route.path === '/inicio' }">Inicio</RouterLink>
      <RouterLink to="/historial" :class="{ active: route.path.startsWith('/historial') }">Historial</RouterLink>
      <RouterLink class="interpret-link" to="/carga">Nueva interpretación <span>＋</span></RouterLink>
    </nav>
    <!-- Enlaces públicos para conocer el proyecto, acceder o crear una cuenta. -->
    <nav v-else aria-label="Navegación principal">
      <RouterLink to="/#acerca">Acerca de</RouterLink><RouterLink to="/acceso">Iniciar sesión</RouterLink><RouterLink class="interpret-link" to="/registro">Crear cuenta</RouterLink>
    </nav>
    <!-- Identidad de demostración mostrada en el área con sesión iniciada. -->
    <RouterLink v-if="loggedInView" class="account" to="/inicio"><span class="avatar">JS</span><span>Juan S.</span><span class="chevron">⌄</span></RouterLink>
  </header>
</template>
<style scoped>
/* Fondo, altura y alineación del encabezado compartido. */
.topbar {
  height:72px;
  background:#071e36;
  border-bottom:1px solid #173d5b;
  display:flex;
  align-items:center;
  padding:0 max(calc((100vw - 1280px)/2),5vw);
  color:#fff;
  gap:28px;
}
.brand {
  display:flex;
  align-items:center;
  color:#fff;
  text-decoration:none;
  white-space:nowrap;
}
.topbar nav {
  margin-left:auto;
  display:flex;
  align-items:center;
  gap:8px;
}
.topbar nav a {
  color:#cfdeeb;
  font-size:12px;
  text-decoration:none;
  padding:10px 12px;
  border-radius:6px;
  transition:background .15s ease,color .15s ease;
}
.topbar nav a:hover,.topbar nav a.active {
  background:#12395b;
  color:#fff;
  text-decoration:none;
}
.topbar nav .interpret-link {
  background:#00abf5;
  color:#062948;
  font-weight:700;
}
.topbar nav .interpret-link:hover {
  background:#27bafa;
}
.account {
  margin-left:10px;
  display:flex;
  align-items:center;
  gap:10px;
  text-decoration:none;
  color:white;
  font-size:12px;
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
.chevron {
  font-size:15px;
  color:#a9bdcc;
}
/* Ajustes para que los enlaces sigan cabiendo en tablet y móvil. */
@media(max-width:850px) {
  .topbar {
    padding:0 22px;
    gap:14px;
  }
}
@media(max-width:620px) {
  .topbar {
    height:64px;
    padding:0 14px;
    gap:8px;
  }
  .topbar nav {
    gap:3px;
  }
  .topbar nav a {
    font-size:10px;
    padding:9px 7px;
  }
  .account {
    margin-left:4px;
  }
  .account>span:not(.avatar) {
    display:none;
  }
}
</style>
