<script setup>
import { computed } from 'vue'
import { estado } from '../store'

const resultados = computed(() => estado.resultados)
const totalRegiones = computed(() => resultados.value.reduce((n, r) => n + r.respuesta.rois.length, 0))
// Confianza promedio de las imágenes en las que se señaló alguna región
const confianzaProm = computed(() => {
  const c = resultados.value.filter((r) => r.respuesta.rois.length).map((r) => r.respuesta.confianza)
  return c.length ? ((c.reduce((a, b) => a + b, 0) / c.length) * 100).toFixed(1) + '%' : '—'
})
const pct = (v) => (v * 100).toFixed(1) + '%'
</script>

<template>
  <main class="page">
    <p class="eyebrow">INTERPRETACIÓN / {{ estado.id || 'SIN DATOS' }}</p>
    <h1>Resultados de la interpretación</h1>
    <p class="subhead">Resultados experimentales para revisión académica.</p>

    <!-- Si se entra directo a esta URL no hay nada analizado. -->
    <section v-if="!resultados.length" class="panel vacio">
      <p>Todavía no hay imágenes analizadas.</p>
      <RouterLink class="button" to="/carga">Cargar imágenes</RouterLink>
    </section>

    <template v-else>
      <section class="stats">
        <article>
          <span>▧</span><div><small>Imágenes procesadas</small><b>{{ resultados.length }}</b></div>
          <i>En esta interpretación</i>
        </article>
        <article>
          <span>◎</span><div><small>Posibles regiones</small><b>{{ totalRegiones }}</b></div>
          <i>Sugeridas por el modelo</i>
        </article>
        <article>
          <span>◷</span><div><small>Confianza promedio</small><b>{{ confianzaProm }}</b></div>
          <i>Estimación experimental</i>
        </article>
      </section>

      <section class="results-grid">
        <article v-for="(r, i) in resultados" :key="r.respuesta.id" class="panel result-card">
          <!-- Imagen original con las regiones dibujadas encima (coordenadas normalizadas 0-1) -->
          <div class="foto">
            <img :src="r.url" :alt="'Imagen ' + (i + 1)" />
            <div
              v-for="(roi, j) in r.respuesta.rois"
              :key="j"
              class="roi"
              :style="{ left: pct(roi.x), top: pct(roi.y), width: pct(roi.ancho), height: pct(roi.alto) }"
            >
              <span>{{ (roi.confianza * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <h2>
            Imagen {{ String(i + 1).padStart(2, '0') }}
            <span class="status">{{ r.respuesta.rois.length ? 'Región detectada' : 'Completado' }}</span>
          </h2>
          <p v-if="r.respuesta.rois.length">
            {{ r.respuesta.rois.length }} posible(s) región(es) · confianza máxima {{ (r.respuesta.confianza * 100).toFixed(1) }}%.
            La región marcada requiere revisión visual especializada.
          </p>
          <p v-else>No se señaló una región sospechosa en esta imagen.</p>
          <p class="meta">{{ r.nombre }} · {{ r.respuesta.metricas.latencia_ms }} ms</p>
        </article>
      </section>

      <div class="button-row">
        <RouterLink class="button secondary" to="/carga">Analizar otras imágenes</RouterLink>
        <RouterLink class="button" to="/historial">Guardar y volver al historial</RouterLink>
      </div>
    </template>

    <p class="disclaimer">Resultado experimental con fines académicos. No constituye un diagnóstico médico ni reemplaza el criterio de profesionales de la salud.</p>
  </main>
</template>
<style scoped>
/* Rejilla de resultados individuales y sus variaciones en pantallas pequeñas. */
.results-grid {
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:16px;
  margin-top:20px;
}
.result-card {
  padding:13px;
}
.result-card .scope-large {
  height:250px;
  margin:0;
}
.result-card h2 {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin:14px 1px 7px;
  color:var(--navy);
  font-size:13px;
}
.result-card p {
  margin:0 1px 3px;
  color:var(--muted);
  font-size:10px;
  line-height:1.5;
}
.result-card .status {
  white-space:nowrap;
}
.alt {
  filter:hue-rotate(24deg);
}
.button-row {
  display:flex;
  justify-content:flex-end;
  flex-wrap:wrap;
  gap:10px;
  margin-top:17px;
}
@media (max-width:680px) {
  .results-grid {
    grid-template-columns:1fr;
  }
  .result-card .scope-large {
    height:235px;
  }
  .button-row {
    justify-content:stretch;
  }
  .button-row .button {
    flex:1 1 100%;
  }
}
.foto {
  position:relative;
  overflow:hidden;
  border-radius:7px;
  background:#0b1f33;
  line-height:0;
}
.foto img {
  display:block;
  width:100%;
  max-height:340px;
  object-fit:contain;
}
.roi {
  position:absolute;
  box-sizing:border-box;
  border:2px solid #00dc78;
  box-shadow:0 0 0 2px #00dc7833;
}
.roi span {
  position:absolute;
  left:-2px;
  top:-17px;
  padding:1px 5px;
  background:#00dc78;
  color:#04230f;
  font-size:10px;
  font-weight:700;
  line-height:15px;
}
.meta {
  opacity:.8;
}
.vacio {
  margin-top:20px;
  padding:30px;
  text-align:center;
}
</style>
