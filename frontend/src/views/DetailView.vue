<script setup>
import PageHead from '../components/PageHead.vue'

// El identificador y los datos de este detalle son estáticos en la maqueta actual.
</script>

<template>
  <main class="page">
    <!-- Identifica el caso y explica qué información incluye esta vista. -->
    <PageHead
      eyebrow="CUADERNO ACADÉMICO / HISTORIAL / A-DEMO-003"
      title="Detalle de interpretación"
      description="Consulta la información y las imágenes del análisis seleccionado."
    />

    <section class="detail-layout">
      <!-- Área visual: imagen principal y miniaturas del caso. -->
      <article class="panel detail-image">
        <h2>Imágenes de la interpretación</h2>
        <p>Colonoscopia · Caso de práctica</p>
        <div class="scope-large"><i></i><span>Región de interés</span></div>
        <div class="thumb-row">
          <div class="scope-thumb"><i></i></div>
          <div class="scope-thumb"><i></i></div>
          <div class="scope-thumb"><i></i></div>
        </div>
      </article>

      <!-- Panel lateral con metadatos y acceso a los resultados. -->
      <aside class="panel side-info">
        <p class="eyebrow">INFORMACIÓN DEL ANÁLISIS</p>
        <h2>A-DEMO-003</h2>
        <dl>
          <dt>Fecha</dt><dd>18 oct 2025 · 10:42 a. m.</dd>
          <dt>Imágenes</dt><dd>3 imágenes</dd>
          <dt>Confianza estimada</dt><dd>94.2% · Alta</dd>
          <dt>Modelo</dt><dd>Experimental 1.0</dd>
          <dt>Estado</dt><dd><span class="status">Completado</span></dd>
        </dl>
        <RouterLink class="button" to="/resultados/A-DEMO-003">Ver interpretación →</RouterLink>
      </aside>
    </section>

    <!-- Aclaración sobre la clasificación experimental. -->
    <p class="disclaimer">ⓘ　La clasificación experimental no reemplaza la evaluación de un profesional de salud.</p>
  </main>
</template>
<style scoped>
/* Coloca la imagen y la ficha de información en dos columnas. */
.detail-layout {
  display:grid;
  grid-template-columns:minmax(0,1.45fr) minmax(260px,.8fr);
  gap:16px;
}
.detail-image,.side-info {
  padding:18px;
}
.detail-image h2,.side-info h2 {
  margin:0 0 7px;
  color:var(--navy);
  font-size:14px;
}
.detail-image > p {
  margin:0;
  color:var(--muted);
  font-size:10px;
}
.detail-image .scope-large {
  height:clamp(255px,32vw,370px);
  margin-top:14px;
}
.thumb-row {
  display:flex;
  gap:8px;
  margin-top:10px;
}
.thumb-row .scope-thumb {
  width:65px;
  height:55px;
}
.side-info .eyebrow {
  margin-bottom:8px;
}
.side-info dl {
  display:grid;
  grid-template-columns:minmax(90px,.8fr) minmax(0,1.2fr);
  row-gap:15px;
  margin:22px 0;
  font-size:10px;
}
.side-info dt {
  color:var(--muted);
}
.side-info dd {
  margin:0;
  color:var(--ink);
  text-align:right;
}
@media (max-width:720px) {
  .detail-layout {
    grid-template-columns:1fr;
  }
  .detail-image .scope-large {
    height:270px;
  }
}
@media (max-width:620px) {
  .detail-image,.side-info {
    padding:14px;
  }
  .side-info dl {
    row-gap:12px;
  }
}
</style>
