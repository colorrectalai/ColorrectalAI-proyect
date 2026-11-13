<script setup>
// compact reduce el tamaño del isotipo y el texto; tagline muestra el lema opcional.
defineProps({ compact: { type: Boolean, default: false }, tagline: { type: Boolean, default: false } })
</script>
<template>
  <!-- Bloque de marca reutilizable en la navegación, acceso y paneles. -->
  <span class="brand-lockup" :class="{ compact }">
    <!-- Isotipo PNG oficial; el nombre de marca se mantiene como texto accesible. -->
    <img class="brand-emblem" src="/img/Logotipo.png" alt="" aria-hidden="true" />
    <span class="brand-wording">
      <span class="brand-name">Colorrectal<span>AI</span>
    </span><small v-if="tagline">TECNOLOGÍA QUE ANALIZA · CIENCIA QUE PREVIENE</small></span>
  </span>
</template>

<style scoped>
/* Alineación del isotipo y la palabra ColorrectalAI en el componente compartido. */
.brand-lockup {
  display:inline-flex;
  align-items:center;
  gap:9px;
  min-width:0;
}
.brand-emblem {
  display:block;
  width:40px;
  height:40px;
  flex:0 0 auto;
  object-fit:contain;
}
.brand-wording {
  display:flex;
  flex-direction:column;
  gap:2px;
  min-width:0;
  margin-left: -3px;
}
.brand-name {
  color:#fff;
  font-weight:700;
  letter-spacing:-.45px;
  font-size:18px;
  line-height:1.05;
  white-space:nowrap;
}
.brand-name>span {
  color:#00abf5;
}
.brand-lockup small {
  color:#b4d9ed;
  font-size:7px;
  letter-spacing:.95px;
  line-height:1.3;
  white-space:nowrap;
}
.brand-lockup.compact .brand-emblem {
  width:40px;
  height:40px;
}
.brand-lockup.compact .brand-name {
  font-size:17px;
}
</style>
