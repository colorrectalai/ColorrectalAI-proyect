<script setup>
import { useRoute } from 'vue-router'
import MainNav from './components/MainNav.vue'

// Permite consultar la ruta actual para decidir qué navegación mostrar.
const route = useRoute()
</script>

<template>
  <!-- La barra se oculta en acceso, registro y análisis para darles una vista limpia. -->
  <MainNav v-if="!['/acceso', '/registro', '/analizando'].includes(route.path)" />

  <!-- Vue Router dibuja aquí la vista correspondiente a la URL actual. -->
  <RouterView />
</template>
