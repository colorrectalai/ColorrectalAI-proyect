<template>
    <!-- Contenedor y título de la pantalla de comparación. -->
    <main class="page">
        <p class="eyebrow">RESULTADOS / A-DEMO-003</p>
        <h1>Comparación general</h1>
        <p class="subhead">Comparación visual de imágenes originales, máscaras de segmentación y superposiciones de región.</p>
        <!-- Tarjetas generadas con v-for: cada una muestra una imagen y su estimación. -->
        <div class="compare-grid">
            <article v-for="n in 3" :key="n" class="panel compare-card">
                <!-- Imagen de muestra; el borde representa la región que se revisaría. -->
                <div class="scope-large">
                    <i></i>
                    <span>Imagen {{ n }}</span>
                </div>
                <!-- La segunda tarjeta usa una clasificación de ejemplo distinta. -->
                <h2>{{ n===2?'Sin hallazgos':'Posible región de interés' }}</h2>
                <!-- Porcentaje y barra visual para comparar la confianza experimental. -->
                <div class="confidence">
                    <span>Confianza del modelo</span>
                    <b>{{ n===2?'91.8':'94.2' }}%</b>
                </div>
                <div class="bar">
                    <i></i>
                </div>
            </article>
        </div>
        <!-- Recordatorio de que la comparación no es un diagnóstico. -->
        <p class="disclaimer">Comparación experimental. La interpretación final debe realizarla un profesional de salud.</p>
    </main>
</template>
<style scoped>
/* Rejilla de las imágenes comparadas y sus tarjetas. */
.compare-grid {
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:15px;
  margin-top:23px;
}
.compare-card {
  padding:12px;
}
.compare-card .scope-large {
  height:230px;
  margin:0;
}
.compare-card h2 {
  min-height:35px;
  margin:13px 1px 10px;
  color:var(--navy);
  font-size:12px;
}
.confidence {
  display:flex;
  justify-content:space-between;
  gap:8px;
  color:var(--muted);
  font-size:10px;
}
.confidence b {
  color:var(--navy);
}
.bar {
  height:6px;
  overflow:hidden;
  margin-top:8px;
  border-radius:6px;
  background:#e8f0f4;
}
.bar i {
  display:block;
  width:64%;
  height:100%;
  border-radius:inherit;
  background:var(--brand);
}
.compare-card:nth-child(2) .bar i {
  width:91.8%;
  background:var(--teal);
}
.compare-card:nth-child(3) .bar i {
  width:76%;
  background:#5f9cbc;
}
@media (max-width:850px) {
  .compare-grid {
    grid-template-columns:repeat(2,minmax(0,1fr));
  }
}
@media (max-width:620px) {
  .compare-grid {
    grid-template-columns:1fr;
  }
  .compare-card .scope-large {
    height:250px;
  }
}
</style>
