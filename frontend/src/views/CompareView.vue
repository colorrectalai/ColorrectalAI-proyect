<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { estado } from '../store'
import { listarInterpretaciones, restaurarInterpretacion } from '../history'
import { tonoFondoROI } from '../roiContraste'

// Comparación de la interpretación actual (la que se acaba de analizar o se reabrió del historial).
const resultados = computed(() => estado.resultados)
const cargando = ref(false)

// Si se entra directo a /comparacion (o se recarga la página), la interpretación en memoria se
// pierde: se abre la más reciente del historial local para no mostrar la página vacía.
onMounted(async () => {
  if (resultados.value.length) return
  cargando.value = true
  try {
    const [masReciente] = await listarInterpretaciones()
    if (masReciente) await restaurarInterpretacion(masReciente.id)
  } catch (e) {
    console.warn('No se pudo abrir la interpretación más reciente:', e)
  } finally {
    cargando.value = false
  }
})
// Primero las imágenes con región detectada, que son las que tienen máscara para comparar.
const ordenados = computed(() =>
  [...resultados.value].sort((a, b) => (b.respuesta.rois?.length || 0) - (a.respuesta.rois?.length || 0)),
)

// Borde claro sobre tejido oscuro y oscuro sobre tejido claro (CP-14, ≥ 3:1).
const tonosROI = reactive({})
watch(resultados, (lista) => {
  lista.forEach((resultado) => {
    ;(resultado.respuesta.rois || []).forEach(async (roi, indice) => {
      const clave = `${resultado.respuesta.id}:${indice}`
      if (!(clave in tonosROI)) tonosROI[clave] = await tonoFondoROI(resultado.url, roi)
    })
  })
}, { immediate: true })

const porcentaje = (valor = 0) => `${(valor * 100).toFixed(1)}%`
// Los tres paneles comparten la proporción de la imagen original: original, máscara y
// superposición quedan alineados píxel a píxel (la API devuelve las máscaras con esa proporción).
const proporcion = (resultado) => {
  const { imagen_ancho: ancho, imagen_alto: alto } = resultado.respuesta
  return { aspectRatio: ancho && alto ? `${ancho} / ${alto}` : '4 / 3' }
}
const estiloROI = (roi) => ({
  left: porcentaje(roi.x), top: porcentaje(roi.y), width: porcentaje(roi.ancho), height: porcentaje(roi.alto),
})
const clasificacion = (resultado) =>
  resultado.respuesta.clasificacion === 'posible_region' ? 'Posible región de interés' : 'Sin hallazgos relevantes'
</script>

<template>
  <main class="page">
    <p class="eyebrow">COMPARACIÓN <span>/</span> {{ estado.id || 'SIN INTERPRETACIÓN' }}</p>
    <h1>Comparación visual</h1>
    <p class="subhead">Imagen original, máscara de segmentación y superposición de la región, alineadas para cada imagen.</p>

    <!-- Sin interpretación activa: se invita a analizar o a abrir una del historial. -->
    <section v-if="cargando" class="panel compare-empty">
      <h2>Abriendo la interpretación más reciente…</h2>
    </section>

    <section v-else-if="!resultados.length" class="panel compare-empty">
      <h2>No hay una interpretación para comparar</h2>
      <p>Analiza imágenes o abre una interpretación guardada para ver la comparación.</p>
      <div class="compare-actions">
        <RouterLink class="button" to="/carga">Cargar imágenes</RouterLink>
        <RouterLink class="button secondary" to="/historial">Abrir historial</RouterLink>
      </div>
    </section>

    <article v-for="resultado in ordenados" v-else :key="resultado.respuesta.id" class="panel compare-row">
      <header class="compare-head">
        <div>
          <h2 :title="resultado.nombre">{{ resultado.nombre }}</h2>
          <p>{{ clasificacion(resultado) }} · Confianza del modelo {{ porcentaje(resultado.respuesta.confianza) }}</p>
        </div>
        <span class="tag" :class="{ found: resultado.respuesta.rois?.length }">
          {{ resultado.respuesta.rois?.length || 0 }} {{ resultado.respuesta.rois?.length === 1 ? 'región' : 'regiones' }}
        </span>
      </header>

      <div class="compare-grid">
        <figure>
          <div class="stage" :style="proporcion(resultado)">
            <img :src="resultado.url" :alt="`Imagen original: ${resultado.nombre}`" />
          </div>
          <figcaption>Imagen original</figcaption>
        </figure>

        <figure>
          <div class="stage mask-stage" :style="proporcion(resultado)">
            <img v-if="resultado.respuesta.mascara_bn" :src="resultado.respuesta.mascara_bn"
                 :alt="`Máscara de segmentación: ${resultado.nombre}`" />
            <p v-else class="no-mask">
              {{ resultado.respuesta.rois?.length ? 'El modelo actual no entrega máscara' : 'Sin región: máscara vacía' }}
            </p>
          </div>
          <figcaption>Máscara de segmentación</figcaption>
        </figure>

        <figure>
          <div class="stage" :style="proporcion(resultado)">
            <img :src="resultado.url" alt="" />
            <img v-if="resultado.respuesta.mascara_resultado" class="overlay" :src="resultado.respuesta.mascara_resultado"
                 :alt="`Máscara superpuesta: ${resultado.nombre}`" />
            <span v-for="(roi, indice) in resultado.respuesta.rois" :key="indice" class="roi" :class="{ 'sobre-fondo-oscuro': tonosROI[`${resultado.respuesta.id}:${indice}`] === 'oscuro' }" :style="estiloROI(roi)"></span>
          </div>
          <figcaption>Superposición (máscara y región)</figcaption>
        </figure>
      </div>
    </article>

    <!-- Recordatorio de que la comparación no es un diagnóstico. -->
    <p class="disclaimer">Comparación experimental. La interpretación final debe realizarla un profesional de salud.</p>
  </main>
</template>

<style scoped>
.compare-empty {
  margin-top:23px;
  padding:24px;
  text-align:center;
}
.compare-empty h2 {
  margin:0 0 6px;
  color:var(--navy);
  font-size:16px;
}
.compare-empty p {
  margin:0;
  color:var(--muted);
  font-size:13px;
}
.compare-actions {
  display:flex;
  justify-content:center;
  gap:10px;
  margin-top:16px;
}
.compare-row {
  margin-top:18px;
  padding:14px;
}
.compare-head {
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:12px;
  margin-bottom:12px;
}
.compare-head h2 {
  margin:0;
  overflow:hidden;
  color:var(--navy);
  font-size:14px;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.compare-head p {
  margin:3px 0 0;
  color:var(--muted);
  font-size:12px;
}
.tag {
  flex:none;
  padding:4px 10px;
  border-radius:20px;
  background:#eef3f7;
  color:var(--muted);
  font-size:11px;
  font-weight:600;
}
.tag.found {
  background:var(--amber-soft);
  color:#7a4a12;
}
.compare-grid {
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:12px;
}
figure {
  margin:0;
}
.stage {
  position:relative;
  overflow:hidden;
  border-radius:10px;
  background:#0b1f33;
}
.stage img {
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:fill;
}
.mask-stage {
  display:grid;
  place-items:center;
}
.no-mask {
  margin:0;
  padding:12px;
  color:#dbe7f1;
  font-size:12px;
  text-align:center;
}
.overlay {
  pointer-events:none;
}
/* Trazo doble de la región: oscuro para tejido claro y halo cian para zonas oscuras (CP-14). */
.roi {
  position:absolute;
  box-sizing:border-box;
  border:2px solid #0b1f33;
  border-radius:6px;
  box-shadow:0 0 0 2px #05c5de;
  pointer-events:none;
}
.roi.sobre-fondo-oscuro {
  border-color:#ffffff;
  box-shadow:0 0 0 2px #0b1f33;
}
figcaption {
  margin-top:6px;
  color:var(--muted);
  font-size:12px;
  text-align:center;
}
@media (max-width:760px) {
  .compare-grid {
    grid-template-columns:1fr;
  }
  .compare-card .scope-large {
    height:min(68vw,300px);
    min-height:220px;
  }
}
</style>
