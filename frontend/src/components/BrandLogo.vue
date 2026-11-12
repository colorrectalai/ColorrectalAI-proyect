<script setup>
// compact reduce el tamaño del logo; tagline muestra el lema bajo el nombre.
defineProps({ compact: { type: Boolean, default: false }, tagline: { type: Boolean, default: false } })
</script>
<template>
  <!-- Bloque de marca reutilizable en la navegación, acceso y paneles. -->
  <span class="brand-lockup" :class="{ compact }">
    <!-- Símbolo vectorial del logo: degradados, cinta y puntos decorativos. -->
    <svg class="brand-emblem" viewBox="0 0 104 100" role="img" aria-label="Símbolo ColorrectalAI">
      <defs><linearGradient id="brandRibbon" x1="10" y1="8" x2="88" y2="88" gradientUnits="userSpaceOnUse"><stop stop-color="#26d4ef"/><stop offset=".52" stop-color="#00abf5"/><stop offset="1" stop-color="#1267db"/></linearGradient><linearGradient id="brandRibbon2" x1="22" y1="12" x2="70" y2="88" gradientUnits="userSpaceOnUse"><stop stop-color="#0089ed"/><stop offset="1" stop-color="#36d9ef"/></linearGradient></defs>
      <path d="M23 54C9 43 14 20 33 17c13-2 20 9 31 9 9 0 16-11 25-10 12 1 14 16 5 23-8 6-18 3-20 16-2 11 4 18 0 27-5 10-18 9-22 0-5-11 5-19 3-29-1-8-9-13-18-9-7 3-8 14-15 17-7 3-13-1-14-7-1-7 6-12 15-16Z" fill="none" stroke="url(#brandRibbon)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M24 54c8-5 18 0 25 8 6 7 4 17 1 25" fill="none" stroke="url(#brandRibbon2)" stroke-width="10" stroke-linecap="round"/>
      <rect x="90" y="20" width="7" height="7" rx="1.5" fill="#0871d6"/><rect x="82" y="34" width="8" height="8" rx="1.5" fill="#008fe9"/><rect x="93" y="42" width="8" height="8" rx="1.5" fill="#00abf5"/><rect x="84" y="53" width="9" height="9" rx="1.5" fill="#19c8ea"/><rect x="94" y="66" width="7" height="7" rx="1.5" fill="#008fe9"/><rect x="84" y="76" width="6" height="6" rx="1.5" fill="#0871d6"/>
    </svg>
    <!-- Nombre de la marca y lema opcional. -->
    <span class="brand-wording"><span class="brand-name">Colorrectal<span>AI</span></span><small v-if="tagline">TECNOLOGÍA QUE ANALIZA · CIENCIA QUE PREVIENE</small></span>
  </span>
</template>
<style scoped>
/* Alineación del símbolo y el nombre; las variantes compactas se usan en barras y tarjetas. */
.brand-lockup {
  display:inline-flex;
  align-items:center;
  gap:9px;
  min-width:0;
}
.brand-emblem {
  display:block;
  width:36px;
  height:36px;
  flex:0 0 auto;
}
.brand-wording {
  display:flex;
  flex-direction:column;
  gap:2px;
  min-width:0;
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
  width:33px;
  height:33px;
}
.brand-lockup.compact .brand-name {
  font-size:17px;
}
</style>
