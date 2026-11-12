<script setup>
// Datos que cada vista entrega al encabezado; el botón es opcional.
defineProps({ title: String, eyebrow: String, description: String, action: String, to: String })
</script>
<template>
  <!-- Encabezado uniforme con etiqueta, título y descripción de la vista. -->
  <header class="page-head">
    <div>
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p class="subhead">{{ description }}</p>
    </div>

    <!-- Si se entrega action, aparece el botón; to permite cambiar su destino. -->
    <RouterLink v-if="action" class="button" :to="to || '/carga'">＋ {{ action }}</RouterLink>
  </header>
</template>
