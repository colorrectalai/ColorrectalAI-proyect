<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { ArrowRight, FileImage, Images, Info, ScanSearch } from '@lucide/vue'
import { estado } from '../store'

const resultados = computed(() => estado.resultados)
const vista = ref('individual')
const indiceActual = ref(0)
const resultadoActual = computed(() => resultados.value[indiceActual.value] || null)
const visorAmpliado = ref(false)
const visualAmpliado = ref('roi')
const zoomActual = ref(1)
const desplazamientoImagen = ref({ x: 0, y: 0 })
const arrastreImagen = ref(null)
const escenarioAmpliado = ref(null)
let desbordamientoAnterior = ''

// Resume las detecciones de toda la interpretación para la vista panorámica.
const totalRegiones = computed(() =>
  resultados.value.reduce((total, resultado) => total + (resultado.respuesta.rois?.length || 0), 0),
)
const imagenesConHallazgos = computed(
  () => resultados.value.filter((resultado) => resultado.respuesta.rois?.length).length,
)
const confianzaPromedio = computed(() => {
  if (!resultados.value.length) return '0.0%'
  const total = resultados.value.reduce((suma, resultado) => suma + resultado.respuesta.confianza, 0)
  return `${((total / resultados.value.length) * 100).toFixed(1)}%`
})

// Mantiene los valores del servicio en escala porcentual para etiquetas y barras.
const porcentaje = (valor = 0) => `${(valor * 100).toFixed(1)}%`
const anchoBarra = (valor = 0) => ({ width: `${Math.max(0, Math.min(valor * 100, 100))}%` })
// Corrige las coordenadas ROI cuando las miniaturas recortan la imagen con object-fit: cover.
const estiloROIEnMiniatura = (roi, resultado, aspectoContenedor) => {
  const { imagen_ancho: ancho, imagen_alto: alto } = resultado.respuesta
  if (!ancho || !alto) {
    return { left: porcentaje(roi.x), top: porcentaje(roi.y), width: porcentaje(roi.ancho), height: porcentaje(roi.alto) }
  }

  const aspectoImagen = ancho / alto
  let x = roi.x
  let y = roi.y
  let width = roi.ancho
  let height = roi.alto

  if (aspectoImagen > aspectoContenedor) {
    const porcionVisible = aspectoContenedor / aspectoImagen
    x = (x - (1 - porcionVisible) / 2) / porcionVisible
    width /= porcionVisible
  } else if (aspectoImagen < aspectoContenedor) {
    const porcionVisible = aspectoImagen / aspectoContenedor
    y = (y - (1 - porcionVisible) / 2) / porcionVisible
    height /= porcionVisible
  }

  return { left: porcentaje(x), top: porcentaje(y), width: porcentaje(width), height: porcentaje(height) }
}
const clasificacion = (resultado) =>
  resultado.respuesta.clasificacion === 'posible_region'
    ? 'Posible pólipo'
    : 'Sin hallazgos relevantes'
const tieneHallazgo = (resultado) => Boolean(resultado.respuesta.rois?.length)

// Permite recorrer las imágenes en ambos sentidos desde el visor individual.
const seleccionarImagen = (indice) => {
  indiceActual.value = (indice + resultados.value.length) % resultados.value.length
}
const mostrarImagen = (indice) => {
  seleccionarImagen(indice)
  vista.value = 'individual'
}

// Abre un visor de pantalla completa con alternancia entre ROI, máscara y superposición.
const abrirVisor = () => {
  if (visorAmpliado.value) return
  visualAmpliado.value = 'roi'
  reiniciarZoom()
  desbordamientoAnterior = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  visorAmpliado.value = true
  window.addEventListener('keydown', cerrarConEscape)
}
const cerrarVisor = () => {
  if (!visorAmpliado.value) return
  visorAmpliado.value = false
  reiniciarZoom()
  document.body.style.overflow = desbordamientoAnterior
  window.removeEventListener('keydown', cerrarConEscape)
}
const cerrarConEscape = (evento) => {
  if (evento.key === 'Escape') cerrarVisor()
}
const ajustarZoom = (cambio, punto = null) => {
  const zoomAnterior = zoomActual.value
  const zoomNuevo = Math.max(1, Math.min(4, Number((zoomAnterior + cambio).toFixed(2))))
  const rect = escenarioAmpliado.value?.getBoundingClientRect()

  if (!rect || zoomNuevo === zoomAnterior) return

  // Conserva bajo el cursor el mismo punto de la imagen mientras cambia el zoom.
  const anclaX = punto ? punto.x - rect.left - rect.width / 2 : 0
  const anclaY = punto ? punto.y - rect.top - rect.height / 2 : 0
  desplazamientoImagen.value = zoomNuevo === 1
    ? { x: 0, y: 0 }
    : {
        x: anclaX - ((anclaX - desplazamientoImagen.value.x) * zoomNuevo) / zoomAnterior,
        y: anclaY - ((anclaY - desplazamientoImagen.value.y) * zoomNuevo) / zoomAnterior,
      }
  zoomActual.value = zoomNuevo
}
const ajustarZoomConRueda = (evento) =>
  ajustarZoom(evento.deltaY < 0 ? 0.2 : -0.2, { x: evento.clientX, y: evento.clientY })
const reiniciarZoom = () => {
  zoomActual.value = 1
  desplazamientoImagen.value = { x: 0, y: 0 }
  arrastreImagen.value = null
}
const estiloZoom = computed(() => ({
  transform: `translate(${desplazamientoImagen.value.x}px, ${desplazamientoImagen.value.y}px) scale(${zoomActual.value})`,
}))
const iniciarArrastre = (evento) => {
  if (zoomActual.value <= 1) return
  arrastreImagen.value = {
    x: evento.clientX - desplazamientoImagen.value.x,
    y: evento.clientY - desplazamientoImagen.value.y,
  }
  evento.currentTarget.setPointerCapture(evento.pointerId)
}
const moverArrastre = (evento) => {
  if (!arrastreImagen.value) return
  desplazamientoImagen.value = {
    x: evento.clientX - arrastreImagen.value.x,
    y: evento.clientY - arrastreImagen.value.y,
  }
}
const terminarArrastre = () => { arrastreImagen.value = null }
onBeforeUnmount(cerrarVisor)
</script>

<template>
  <main class="page results-page">
    <!-- Encabezado de la interpretación recién procesada. -->
    <header class="results-heading">
      <p class="eyebrow">INTERPRETACIÓN <span>/</span> {{ estado.id || 'RESULTADOS' }}</p>
      <h1>Resultados del análisis</h1>
      <p class="subhead">
        {{ resultados.length
          ? `Revisión experimental de ${resultados.length} ${resultados.length === 1 ? 'imagen' : 'imágenes'} de endoscopia.`
          : 'Resultados experimentales para revisión académica.' }}
      </p>
    </header>

    <!-- Imágenes que la API rechazó: el resto del lote se analizó igual (CF-02). -->
    <section v-if="estado.fallidos?.length" class="rejected-files" role="alert">
      <h2>
        {{ estado.fallidos.length === 1 ? 'Una imagen no se pudo analizar' : `${estado.fallidos.length} imágenes no se pudieron analizar` }}
      </h2>
      <ul>
        <li v-for="fallo in estado.fallidos" :key="fallo.nombre">
          <strong>{{ fallo.nombre }}:</strong> {{ fallo.mensaje }}
        </li>
      </ul>
    </section>

    <!-- Estado vacío para accesos directos o cuando aún no hay una interpretación. -->
    <section v-if="!resultados.length" class="empty-state">
      <FileImage aria-hidden="true" />
      <h2>Todavía no hay imágenes analizadas</h2>
      <p>Carga una o varias imágenes para revisar los resultados experimentales.</p>
      <RouterLink class="button" to="/carga">Cargar imágenes <ArrowRight aria-hidden="true" /></RouterLink>
    </section>

    <template v-else>
      <!-- Modo individual: imagen principal y navegación en miniaturas. -->
      <template v-if="vista === 'individual' && resultadoActual">
        <div id="panel-individual" class="individual-layout" role="tabpanel" aria-labelledby="tab-individual">
          <section class="image-section">
          <div class="section-heading result-visual-heading">
            <div class="view-selector" role="tablist" aria-label="Tipo de vista de resultados">
              <button id="tab-individual" class="view-tab" :class="{ active: vista === 'individual' }" type="button" role="tab" :aria-selected="vista === 'individual'" aria-controls="panel-individual" @click="vista = 'individual'">
                <FileImage aria-hidden="true" /> Vista individual
              </button>
              <button id="tab-general" class="view-tab" :class="{ active: vista === 'general' }" type="button" role="tab" :aria-selected="vista === 'general'" aria-controls="panel-general" @click="vista = 'general'">
                <Images aria-hidden="true" /> Vista general
              </button>
            </div>
            <div class="current-image-meta" aria-live="polite">
              <strong :title="resultadoActual.nombre">{{ resultadoActual.nombre }}</strong>
              <span class="meta-divider" aria-hidden="true">|</span>
              <span>{{ indiceActual + 1 }} de {{ resultados.length }} imágenes</span>
            </div>
          </div>

          <!-- La ROI se dibuja sobre la imagen original usando coordenadas normalizadas de la API.
               Con el modelo de segmentación, al lado se muestra la máscara en blanco y negro. -->
          <div
            class="image-stage"
            :class="{ 'con-mascara-bn': resultadoActual.respuesta.mascara_bn }"
            role="button"
            tabindex="0"
            :aria-label="`Ampliar la imagen y sus resultados: ${resultadoActual.nombre}`"
            @click="abrirVisor"
            @keydown.enter.space.prevent="abrirVisor"
          >
            <figure class="visor-panel">
              <div class="image-frame">
                <img :src="resultadoActual.url" :alt="`Imagen endoscópica ${indiceActual + 1}`" />
                <div
                  v-for="(roi, roiIndex) in resultadoActual.respuesta.rois"
                  :key="roiIndex"
                  class="roi-box"
                  :style="{ left: porcentaje(roi.x), top: porcentaje(roi.y), width: porcentaje(roi.ancho), height: porcentaje(roi.alto) }"
                >
                  <span>ROI {{ String(roiIndex + 1).padStart(2, '0') }}</span>
                </div>
              </div>
                <figcaption>Imagen con ROI · clic para ampliar</figcaption>
            </figure>

            <figure v-if="resultadoActual.respuesta.mascara_bn" class="visor-panel">
              <div class="image-frame">
                <img class="mascara-bn" :src="resultadoActual.respuesta.mascara_bn" alt="Máscara de segmentación en blanco y negro" />
              </div>
              <figcaption>Máscara de segmentación</figcaption>
            </figure>
          </div>

          <!-- Controles de imagen anterior/siguiente y selección directa. -->
          <div class="image-navigation">
            <button class="navigation-button" type="button" :disabled="resultados.length < 2" @click="seleccionarImagen(indiceActual - 1)">
              <span aria-hidden="true">←</span> Imagen anterior
            </button>
            <div class="thumbnails" aria-label="Imágenes de esta interpretación">
              <button
                v-for="(resultado, indice) in resultados"
                :key="resultado.respuesta.id"
                class="thumbnail"
                :class="{ selected: indice === indiceActual }"
                type="button"
                :aria-label="`Ver imagen ${indice + 1}: ${resultado.nombre}`"
                :aria-pressed="indice === indiceActual"
                @click="seleccionarImagen(indice)"
              >
                <img :src="resultado.respuesta.imagen_resultado || resultado.url" :alt="''" />
                <span>{{ String(indice + 1).padStart(2, '0') }}</span>
              </button>
            </div>
            <button class="navigation-button next-button" type="button" :disabled="resultados.length < 2" @click="seleccionarImagen(indiceActual + 1)">
              Siguiente imagen <span aria-hidden="true">→</span>
            </button>
          </div>
          </section>

          <!-- Resultados de la imagen seleccionada junto al visor en escritorio. -->
          <section class="interpretation-section individual-results" aria-labelledby="individual-results-title">
          <div class="section-heading results-section-heading">
            <div>
              <h2 id="individual-results-title">Lectura del modelo</h2>
            </div>
          </div>

          <div class="finding-banner" :class="{ clear: !tieneHallazgo(resultadoActual) }">
            <span class="finding-mark" aria-hidden="true">{{ tieneHallazgo(resultadoActual) ? '✓' : '–' }}</span>
            <div>
              <strong>{{ tieneHallazgo(resultadoActual) ? 'Posible región de interés' : 'Sin hallazgos relevantes' }}</strong>
              <p>{{ tieneHallazgo(resultadoActual) ? 'El modelo señaló una región que requiere revisión visual.' : 'El modelo no señaló una región sospechosa en esta imagen.' }}</p>
            </div>
          </div>

          <div class="individual-metrics">
            <article class="confidence-card">
              <span class="metric-label">Confianza del modelo</span>
              <strong>{{ porcentaje(resultadoActual.respuesta.confianza) }}</strong>
              <div class="confidence-track" role="meter" :aria-valuenow="(resultadoActual.respuesta.confianza || 0) * 100" aria-valuemin="0" aria-valuemax="100" aria-label="Confianza experimental">
                <span :style="anchoBarra(resultadoActual.respuesta.confianza)"></span>
              </div>
            </article>

            <article class="detail-metric">
              <span class="metric-icon"><ScanSearch aria-hidden="true" /></span>
              <div><small>Clasificación (experimental)</small><strong>{{ clasificacion(resultadoActual) }}</strong></div>
            </article>
            <article class="detail-metric">
              <span class="metric-icon"><Images aria-hidden="true" /></span>
              <div>
                <small>Regiones de interés</small>
                <strong>{{ resultadoActual.respuesta.rois.length }} {{ resultadoActual.respuesta.rois.length === 1 ? 'región' : 'regiones' }}</strong>
              </div>
            </article>
            <article class="detail-metric">
              <span class="metric-icon"><Info aria-hidden="true" /></span>
              <div><small>Tiempo de procesamiento</small><strong>{{ resultadoActual.respuesta.metricas.latencia_ms }} ms</strong></div>
            </article>
          </div>

          <div v-if="resultadoActual.respuesta.rois.length" class="roi-list">
            <h3>Regiones señaladas</h3>
            <div v-for="(roi, roiIndex) in resultadoActual.respuesta.rois" :key="roiIndex" class="roi-row">
              <span>ROI {{ String(roiIndex + 1).padStart(2, '0') }}</span>
              <div class="confidence-track"><span :style="anchoBarra(roi.confianza)"></span></div>
              <strong>{{ porcentaje(roi.confianza) }}</strong>
            </div>
          </div>
          </section>
        </div>
      </template>

      <!-- Modo general: primero una panorámica de imágenes y después la tabla de resultados. -->
      <template v-else-if="vista === 'general'">
        <section id="panel-general" class="image-section general-images" role="tabpanel" aria-labelledby="tab-general">
          <div class="section-heading result-visual-heading general-visual-heading">
            <div class="view-selector" role="tablist" aria-label="Tipo de vista de resultados">
              <button id="tab-individual" class="view-tab" :class="{ active: vista === 'individual' }" type="button" role="tab" :aria-selected="vista === 'individual'" aria-controls="panel-individual" @click="vista = 'individual'">
                <FileImage aria-hidden="true" /> Vista individual
              </button>
              <button id="tab-general" class="view-tab" :class="{ active: vista === 'general' }" type="button" role="tab" :aria-selected="vista === 'general'" aria-controls="panel-general" @click="vista = 'general'">
                <Images aria-hidden="true" /> Vista general
              </button>
            </div>
            <span class="image-count">{{ resultados.length }} imágenes en esta interpretación</span>
          </div>
          <div class="image-gallery">
            <button
              v-for="(resultado, indice) in resultados"
              :key="resultado.respuesta.id"
              class="gallery-item"
              type="button"
              :aria-label="`Abrir vista individual de ${resultado.nombre}`"
              @click="mostrarImagen(indice)"
            >
              <span class="gallery-image">
                <span v-if="resultado.respuesta.mascara_resultado || resultado.respuesta.mascara_bn" class="general-image-composite">
                  <img :src="resultado.url" :alt="`Imagen endoscópica con segmentación: ${resultado.nombre}`" />
                  <img
                    class="general-mask-overlay"
                    :class="{ 'binary-mask-overlay': !resultado.respuesta.mascara_resultado }"
                    :src="resultado.respuesta.mascara_resultado || resultado.respuesta.mascara_bn"
                    alt=""
                  />
                  <span
                    v-for="(roi, roiIndex) in resultado.respuesta.rois"
                    :key="`galeria-roi-${roiIndex}`"
                    class="general-roi-frame"
                    aria-hidden="true"
                    :style="estiloROIEnMiniatura(roi, resultado, 4 / 3)"
                  ><small>ROI {{ String(roiIndex + 1).padStart(2, '0') }}</small></span>
                </span>
                <img v-else :src="resultado.respuesta.imagen_resultado || resultado.url" :alt="`Resultado de ${resultado.nombre}`" />
                <span class="gallery-index">{{ String(indice + 1).padStart(2, '0') }}</span>
              </span>
              <span class="gallery-caption">
                <strong>{{ resultado.nombre }}</strong>
                <span :class="['mini-status', { detected: tieneHallazgo(resultado) }]">
                  {{ tieneHallazgo(resultado) ? 'Región señalada' : 'Sin hallazgos' }}
                </span>
              </span>
            </button>
          </div>
        </section>

        <!-- Resumen y lista completa con acceso directo a cada interpretación individual. -->
        <section class="interpretation-section general-results" aria-labelledby="general-results-title">
          <div class="section-heading results-section-heading">
            <div>
              <h2 id="general-results-title">Resultados generales</h2>
            </div>
          </div>

          <div class="summary-grid">
            <article class="summary-card">
              <span class="summary-icon"><FileImage aria-hidden="true" /></span>
              <div><small>Imágenes analizadas</small><strong>{{ resultados.length }}</strong></div>
            </article>
            <article class="summary-card">
              <span class="summary-icon"><ScanSearch aria-hidden="true" /></span>
              <div><small>Regiones de interés</small><strong>{{ totalRegiones }}</strong></div>
            </article>
            <article class="summary-card positive-summary">
              <span class="summary-icon" aria-hidden="true">✓</span>
              <div><small>Imágenes con regiones</small><strong>{{ imagenesConHallazgos }}</strong></div>
            </article>
            <article class="summary-card">
              <span class="summary-icon"><Images aria-hidden="true" /></span>
              <div><small>Confianza promedio</small><strong>{{ confianzaPromedio }}</strong></div>
            </article>
          </div>

          <div class="results-table-wrap">
            <table class="results-table">
              <thead>
                <tr>
                  <th scope="col">Imagen</th>
                  <th scope="col">Clasificación experimental</th>
                  <th scope="col">Confianza</th>
                  <th scope="col">Detección</th>
                  <th scope="col"><span class="visually-hidden">Acción</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(resultado, indice) in resultados" :key="resultado.respuesta.id">
                  <td>
                    <div class="table-image-cell">
                      <span class="table-image-name"><strong>{{ resultado.nombre }}</strong><small>Imagen {{ String(indice + 1).padStart(2, '0') }}</small></span>
                      <span class="table-image-pair">
                        <span v-if="resultado.respuesta.mascara_resultado || resultado.respuesta.mascara_bn" class="table-image-composite">
                          <img :src="resultado.url" :alt="`Imagen endoscópica con segmentación: ${resultado.nombre}`" />
                          <img
                            class="general-mask-overlay"
                            :class="{ 'binary-mask-overlay': !resultado.respuesta.mascara_resultado }"
                            :src="resultado.respuesta.mascara_resultado || resultado.respuesta.mascara_bn"
                            alt=""
                          />
                          <span
                            v-for="(roi, roiIndex) in resultado.respuesta.rois"
                            :key="`tabla-roi-${roiIndex}`"
                            class="general-roi-frame"
                            aria-hidden="true"
                            :style="estiloROIEnMiniatura(roi, resultado, 99 / 72)"
                          ><small>ROI {{ String(roiIndex + 1).padStart(2, '0') }}</small></span>
                        </span>
                        <img v-else :src="resultado.respuesta.imagen_resultado || resultado.url" :alt="`Resultado de ${resultado.nombre}`" />
                        <img v-if="resultado.respuesta.mascara_bn" class="table-mask-image" :src="resultado.respuesta.mascara_bn" :alt="`Máscara de segmentación: ${resultado.nombre}`" />
                      </span>
                    </div>
                  </td>
                  <td><span class="classification-chip" :class="{ neutral: !tieneHallazgo(resultado) }"><ScanSearch aria-hidden="true" />{{ clasificacion(resultado) }}</span></td>
                  <td>
                    <div class="table-confidence"><strong>{{ porcentaje(resultado.respuesta.confianza) }}</strong><span class="confidence-track"><span :style="anchoBarra(resultado.respuesta.confianza)"></span></span></div>
                  </td>
                  <td><span class="detection-status" :class="{ clear: !tieneHallazgo(resultado) }">{{ tieneHallazgo(resultado) ? 'Región señalada' : 'No señalada' }}</span></td>
                  <td><button class="row-action" type="button" @click="mostrarImagen(indice)">Ver imagen <ArrowRight aria-hidden="true" /></button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- Visor ampliado: permite comparar la ROI, la máscara binaria y su superposición. -->
      <Teleport to="body">
        <div
          v-if="visorAmpliado && resultadoActual"
          class="image-lightbox"
          role="dialog"
          aria-modal="true"
          aria-label="Visor ampliado de resultados"
          @click="cerrarVisor"
        >
          <section class="lightbox-content">
            <header class="lightbox-header" @click.stop>
              <div>
                <p>REVISIÓN VISUAL</p>
                <h2>{{ resultadoActual.nombre }}</h2>
                <span>Imagen {{ indiceActual + 1 }} de {{ resultados.length }}</span>
              </div>
              <button class="lightbox-close" type="button" aria-label="Cerrar visor ampliado" @click="cerrarVisor">×</button>
            </header>

            <div class="lightbox-tabs" role="tablist" aria-label="Visualización ampliada" @click.stop>
              <button type="button" role="tab" :aria-selected="visualAmpliado === 'roi'" :class="{ active: visualAmpliado === 'roi' }" @click="visualAmpliado = 'roi'">
                Imagen con ROI
              </button>
              <button v-if="resultadoActual.respuesta.mascara_resultado" type="button" role="tab" :aria-selected="visualAmpliado === 'superpuesta'" :class="{ active: visualAmpliado === 'superpuesta' }" @click="visualAmpliado = 'superpuesta'">
                Máscara superpuesta
              </button>
              <button v-if="resultadoActual.respuesta.mascara_bn" type="button" role="tab" :aria-selected="visualAmpliado === 'mascara'" :class="{ active: visualAmpliado === 'mascara' }" @click="visualAmpliado = 'mascara'">
                Máscara B/N
              </button>
            </div>

            <div class="lightbox-zoom-controls" @click.stop>
              <button type="button" aria-label="Alejar imagen" :disabled="zoomActual <= 1" @click="ajustarZoom(-0.25)">−</button>
              <button class="zoom-readout" type="button" aria-label="Restablecer zoom" @click="reiniciarZoom">{{ Math.round(zoomActual * 100) }}%</button>
              <button type="button" aria-label="Acercar imagen" :disabled="zoomActual >= 4" @click="ajustarZoom(0.25)">+</button>
            </div>

            <div ref="escenarioAmpliado" class="lightbox-stage" @wheel.prevent="ajustarZoomConRueda">
              <div
                class="lightbox-image-frame"
                :class="{ zoomed: zoomActual > 1, dragging: arrastreImagen }"
                :style="estiloZoom"
                @pointerdown="iniciarArrastre"
                @pointermove="moverArrastre"
                @pointerup="terminarArrastre"
                @pointercancel="terminarArrastre"
                @click.stop
              >
                <template v-if="visualAmpliado !== 'mascara'">
                  <img :src="resultadoActual.url" :alt="`Imagen endoscópica ampliada ${resultadoActual.nombre}`" />
                  <img v-if="visualAmpliado === 'superpuesta'" class="lightbox-mask-overlay" :src="resultadoActual.respuesta.mascara_resultado" alt="Máscara de segmentación superpuesta" />
                  <template v-if="visualAmpliado === 'roi' || visualAmpliado === 'superpuesta'">
                    <div
                      v-for="(roi, roiIndex) in resultadoActual.respuesta.rois"
                      :key="roiIndex"
                      class="roi-box"
                      :style="{ left: porcentaje(roi.x), top: porcentaje(roi.y), width: porcentaje(roi.ancho), height: porcentaje(roi.alto) }"
                    ><span>ROI {{ String(roiIndex + 1).padStart(2, '0') }}</span></div>
                  </template>
                </template>
                <img v-else class="lightbox-binary-mask" :src="resultadoActual.respuesta.mascara_bn" alt="Máscara de segmentación en blanco y negro" />
              </div>
            </div>
            <p class="lightbox-hint">Usa la rueda o los botones para acercar; arrastra la imagen ampliada. Haz clic fuera para cerrar.</p>
          </section>
        </div>
      </Teleport>

      <!-- Acciones del flujo disponibles después de cualquiera de las dos vistas. -->
      <div class="results-actions">
        <RouterLink class="button secondary" to="/carga">Analizar otras imágenes</RouterLink>
        <RouterLink class="button" to="/historial">Volver al historial <ArrowRight aria-hidden="true" /></RouterLink>
      </div>
    </template>

    <!-- Aviso académico común a las dos modalidades de resultados. -->
    <p class="disclaimer"><Info aria-hidden="true" /> <span>Resultados experimentales para investigación y educación. No constituyen un diagnóstico ni reemplazan la evaluación de un profesional de la salud.</span></p>
  </main>
</template>

<style scoped>
/* Encabezado y jerarquía de contenido de esta vista. */

.results-page {
  max-width: 1440px;
  margin-inline: auto;
  position: relative;   /* Necesario para contener el ::before */
  isolation: isolate;   /* Evita que el z-index: -1 se esconda detrás del body */
  --results-gap: 16px;
  display: block;
  padding-top: 22px;
  padding-bottom: 22px;
}

.results-page::before {
  content: "";
  position: absolute;
  inset: -20px calc((100% - 100vw) / 2); /* Extiende la capa hasta ambos bordes del viewport */
  z-index: -1;
  pointer-events: none;

  background:
    linear-gradient(
      to bottom,
      rgba(243, 248, 253, 0.842) 0%,
      rgba(243, 248, 253, 0.2) 100%
    ),
    url("/img/Fondo4.png") center / cover no-repeat;

  filter: blur(1px);
}

.results-heading {
  margin-bottom: 16px;
}
.results-heading .eyebrow span {
  padding-inline: 4px;
  color: var(--quiet);
}

.results-heading h1 {
  margin: 0 0 6px;
  color: var(--navy-deep);
  font-size: clamp(25px, 2.6vw, 32px);
  line-height: 1.15;
  letter-spacing: -0.045em;
}

.results-heading .subhead {
  font-size: 14px;
}

/* El selector ocupa el espacio libre del encabezado y permanece bajo la navbar al desplazarse. */
.view-selector {
  position: sticky;
  top: 82px;
  z-index: 900;
  display: flex;
  flex: 0 0 auto;
  width: min(100%, 350px);
  gap: 3px;
  margin: 0;
  padding: 4px;
  border: 0;
  border-radius: 13px;
  background: #edf4f9;
  box-shadow: none;
}
.view-tab {
  display: inline-flex;
  flex: 1 1 50%;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 8px 12px;
  border: 0;
  border-radius: 11px;
  background: transparent;
  color: var(--navy);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: color 150ms ease, background-color 150ms ease, box-shadow 150ms ease;
}

.view-tab svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.view-tab:hover:not(.active) {
  background: #f1f8fd;
}

.view-tab.active {
  background: var(--blue);
  color: #fff;
  box-shadow: none;
}

.view-tab:focus-visible {
  position: relative;
  z-index: 1;
  outline: 2px solid var(--navy);
  outline-offset: 2px;
}

/* Imágenes en una superficie limpia, sin fondo ilustrado o decorativo. */
.image-section,
.interpretation-section,
.empty-state {
  border: 1px solid var(--line);
  border-radius: 15px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.image-section {
  padding: 16px;
  margin-bottom: var(--results-gap);
}

/* En escritorio, el visor y sus resultados se leen lado a lado. */
.individual-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  align-items: start;
  gap: var(--results-gap);
  margin-bottom: var(--results-gap);
}

.individual-layout > .image-section,
.individual-layout > .interpretation-section {
  min-width: 0;
  margin-bottom: 0;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-kicker {
  margin: 0 0 5px;
  color: var(--brand);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.section-heading h2 {
  margin: 0;
  color: var(--navy);
  font-size: 20px;
  line-height: 1.3;
  letter-spacing: -0.025em;
}

.image-count {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--muted);
  font-size: 13px;
  white-space: nowrap;
}

.image-count svg {
  width: 17px;
  height: 17px;
  color: var(--brand);
}

/* Encabezado del visor: selector a la izquierda y archivo/posición a la derecha. */
.result-visual-heading {
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.current-image-meta {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
  color: var(--muted);
  font-size: 12px;
  text-align: right;
  white-space: nowrap;
}

.current-image-meta strong {
  display: block;
  max-width: 220px;
  overflow: hidden;
  color: var(--navy);
  font-size: 13px;
  text-overflow: ellipsis;
}

.meta-divider {
  color: var(--quiet);
}

/* Visor de imagen con caja ROI posicionada en coordenadas de la imagen. */
.image-stage {
  display: grid;
  min-height: clamp(210px, 29vh, 285px);
  place-items: center;
  overflow: hidden;
  padding: 10px;
  border: 1px solid #e4ebf0;
  border-radius: 12px;
  background: #f8fafc;
  cursor: zoom-in;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.image-stage:hover,
.image-stage:focus-visible {
  border-color: #7fc8f4;
  box-shadow: 0 0 0 3px rgb(0 157 255 / 12%);
  outline: none;
}

.image-frame {
  position: relative;
  width: fit-content;
  max-width: 100%;
  line-height: 0;
}

.image-frame > img {
  display: block;
  width: auto;
  max-width: 100%;
  max-height: min(36vh, 440px);
  border-radius: 7px;
  object-fit: contain;
}

/* Trazo doble: borde oscuro para contrastar con el tejido claro (≥ 3:1, CP-14) y halo cian
   por fuera para que siga visible sobre zonas oscuras de la imagen. */
.roi-box {
  position: absolute;
  box-sizing: border-box;
  border: 2px solid #0b1f33;
  border-radius: 8px;
  box-shadow: 0 0 0 2px #05c5de, 0 0 0 3px rgb(11 31 51 / 55%);
}

.rejected-files {
  margin: 0 0 18px;
  padding: 14px 18px;
  border: 1px solid #f0c9a6;
  border-radius: 12px;
  background: var(--amber-soft);
  color: var(--ink);
}

.rejected-files h2 {
  margin: 0 0 6px;
  color: #7a4a12;
  font-size: 14px;
}

.rejected-files ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
}

/* Con modelo de segmentación: imagen con ROI y máscara en blanco y negro, lado a lado. */
.image-stage.con-mascara-bn {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.visor-panel {
  display: grid;
  min-width: 0;
  margin: 0;
  gap: 8px;
  justify-items: center;
}

.visor-panel figcaption {
  color: #52606d;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.2;
  text-transform: uppercase;
}

.image-frame > img.mascara-bn {
  border: 1px solid #1f2937;
}

@media (max-width: 560px) {
  .image-stage.con-mascara-bn {
    grid-template-columns: 1fr;
  }
}

.roi-box > span {
  position: absolute;
  top: -24px;
  left: -2px;
  padding: 4px 8px;
  border-radius: 6px 6px 0 0;
  background: #05c5de;
  color: #052538;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

/* Navegación de imágenes y miniaturas bajo el visor. */
.image-navigation {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  margin-top: 15px;
}

.navigation-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 8px 14px;
  border: 1px solid #cbddeb;
  border-radius: 22px;
  background: #fff;
  color: var(--navy);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.navigation-button:hover:not(:disabled) {
  border-color: var(--brand);
  color: var(--brand);
}

.navigation-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.navigation-button span {
  font-size: 18px;
  line-height: 1;
}

.next-button {
  border-color: var(--brand);
  background: var(--brand);
  color: #fff;
}

.next-button:hover:not(:disabled) {
  background: #168ce2;
  color: #fff;
}

.thumbnails {
  display: flex;
  justify-content: center;
  gap: 9px;
  overflow-x: auto;
  padding: 3px;
}

.thumbnail {
  position: relative;
  flex: 0 0 68px;
  width: 68px;
  height: 60px;
  overflow: hidden;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 9px;
  background: #edf2f6;
  cursor: pointer;
}

.thumbnail.selected {
  border-color: var(--brand);
  box-shadow: 0 0 0 2px rgb(0 157 255 / 16%);
}

.thumbnail img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail > span {
  position: absolute;
  right: 4px;
  bottom: 4px;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgb(2 23 45 / 72%);
  color: #fff;
  font-size: 9px;
  font-weight: 700;
}

/* Bloque de interpretación individual y resumen general. */
.interpretation-section {
  padding: 18px;
  margin-bottom: var(--results-gap);
}

.results-section-heading {
  margin-bottom: 18px;
}

.experimental-label {
  padding: 7px 10px;
  border: 1px solid #d6e9f7;
  border-radius: 20px;
  background: #f3f9fe;
  color: #426987;
  font-size: 11px;
  white-space: nowrap;
}

.finding-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 15px 17px;
  border: 1px solid #b9ecdd;
  border-radius: 11px;
  background: #e9faf4;
  color: #155a47;
}

.finding-banner.clear {
  border-color: #dce6ee;
  background: #f5f8fa;
  color: var(--ink);
}

.finding-mark {
  display: grid;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 50%;
  background: #19c993;
  color: #fff;
  font-size: 21px;
  font-weight: 700;
}

.finding-banner.clear .finding-mark {
  background: #8a9aa8;
}

.finding-banner strong {
  display: block;
  font-size: 17px;
}

.finding-banner p {
  margin: 3px 0 0;
  color: inherit;
  font-size: 13px;
  line-height: 1.45;
  opacity: 0.88;
}

.individual-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.confidence-card,
.detail-metric {
  min-height: 94px;
  border: 1px solid #e0e9f0;
  border-radius: 11px;
  background: #fff;
}

.confidence-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 13px 16px;
}

.metric-label,
.confidence-card small {
  color: var(--muted);
  font-size: 12px;
}

.confidence-card > strong {
  margin-top: 2px;
  color: var(--navy);
  font-size: 27px;
  line-height: 1.1;
}

.confidence-track {
  display: block;
  height: 8px;
  overflow: hidden;
  border-radius: 20px;
  background: #dce8f2;
}

.confidence-card .confidence-track {
  margin: 7px 0 5px;
}

.confidence-track > span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--brand);
}

.detail-metric {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 14px;
}

.metric-icon,
.summary-icon {
  display: grid;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 12px;
  background: #e8f5ff;
  color: var(--brand);
}

.metric-icon svg,
.summary-icon svg {
  width: 22px;
  height: 22px;
}

.detail-metric small,
.detail-metric strong {
  display: block;
}

.detail-metric small {
  margin-bottom: 4px;
  color: var(--muted);
  font-size: 11px;
}

.detail-metric strong {
  color: var(--navy);
  font-size: 15px;
}

.roi-list {
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid #e0e9f0;
  border-radius: 11px;
}

.roi-list h3 {
  margin: 0 0 11px;
  color: var(--navy);
  font-size: 14px;
}

.roi-row {
  display: grid;
  grid-template-columns: 100px minmax(70px, 1fr) 54px;
  align-items: center;
  gap: 12px;
  padding: 9px 0;
  border-top: 1px solid #edf2f6;
  color: var(--ink);
  font-size: 12px;
}

.roi-row strong {
  color: var(--navy);
  text-align: right;
}

/* Galería panorámica de las imágenes pertenecientes al análisis. */
.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

.gallery-item {
  min-width: 0;
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: #fff;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
  transition: border-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}

.gallery-item:hover {
  transform: translateY(-2px);
  border-color: #8cccf5;
  box-shadow: 0 7px 18px rgb(22 78 115 / 10%);
}

.gallery-image {
  position: relative;
  display: block;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #f0f4f7;
}

.gallery-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.general-image-composite,
.table-image-composite {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
  overflow: hidden;
  isolation: isolate;
}

.general-image-composite > img,
.table-image-composite > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.general-image-composite > img.general-mask-overlay,
.table-image-composite > img.general-mask-overlay {
  mix-blend-mode: screen;
  opacity: 0.95;
}

.general-image-composite > img.general-mask-overlay.binary-mask-overlay,
.table-image-composite > img.general-mask-overlay.binary-mask-overlay {
  filter: sepia(1) saturate(1000%) hue-rotate(155deg);
  mix-blend-mode: screen;
  opacity: 0.9;
}

.general-roi-frame {
  position: absolute;
  z-index: 1;
  border: 2px solid #0b1f33;
  border-radius: 4px;
  box-shadow: 0 0 0 2px #08c9ed, 0 0 10px rgb(0 197 255 / 45%);
  pointer-events: none;
}

.general-roi-frame small {
  position: absolute;
  top: -15px;
  left: -2px;
  padding: 2px 5px;
  border-radius: 4px 4px 0 0;
  background: #08c9ed;
  color: #02172d;
  font-size: 8px;
  font-weight: 800;
  line-height: 1.15;
  white-space: nowrap;
}

.gallery-index {
  position: absolute;
  top: 9px;
  left: 9px;
  padding: 4px 7px;
  border-radius: 6px;
  background: rgb(2 23 45 / 74%);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

.gallery-caption {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 11px 12px;
}

.gallery-caption > strong {
  overflow: hidden;
  color: var(--navy);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-status,
.detection-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 8px;
  border-radius: 20px;
  background: #e8f5ff;
  color: #12669b;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.mini-status.detected,
.detection-status:not(.clear) {
  background: #e5f8f0;
  color: #137751;
}

/* Visor ampliado sobre un fondo oscuro para comparar la imagen y la máscara. */
.image-lightbox {
  position: fixed;
  inset: 0;
  z-index: 5000;
  display: grid;
  place-items: center;
  overflow: auto;
  padding: 28px;
  background: rgb(2 23 45 / 62%);
  -webkit-backdrop-filter: saturate(0.65) brightness(0.48) blur(3px);
  backdrop-filter: saturate(0.65) brightness(0.48) blur(3px);
  color: #fff;
}

.lightbox-content {
  display: flex;
  width: min(1500px, 100%);
  min-height: min(680px, calc(100vh - 56px));
  flex-direction: column;
  gap: 16px;
}

.lightbox-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.lightbox-header p {
  margin: 0 0 5px;
  color: #42c6ff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.lightbox-header h2 {
  margin: 0;
  color: #fff;
  font-size: clamp(18px, 2vw, 25px);
}

.lightbox-header span,
.lightbox-hint {
  color: #b8c9d8;
  font-size: 12px;
}

.lightbox-close {
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 35%);
  border-radius: 50%;
  background: rgb(255 255 255 / 8%);
  color: #fff;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}

.lightbox-close:hover {
  background: rgb(255 255 255 / 18%);
}

.lightbox-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lightbox-tabs button {
  min-height: 38px;
  padding: 8px 13px;
  border: 1px solid rgb(193 220 242 / 38%);
  border-radius: 20px;
  background: rgb(255 255 255 / 7%);
  color: #e8f4ff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.lightbox-tabs button.active {
  border-color: #009dff;
  background: #078de2;
  color: #fff;
}

.lightbox-zoom-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.lightbox-zoom-controls button {
  display: grid;
  min-width: 38px;
  height: 36px;
  place-items: center;
  padding: 0 10px;
  border: 1px solid rgb(193 220 242 / 38%);
  border-radius: 9px;
  background: rgb(255 255 255 / 8%);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

.lightbox-zoom-controls button:hover:not(:disabled) {
  background: rgb(255 255 255 / 18%);
}

.lightbox-zoom-controls button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.lightbox-zoom-controls .zoom-readout {
  min-width: 64px;
  font-size: 12px;
  font-weight: 600;
}

.lightbox-stage {
  display: grid;
  min-height: 0;
  flex: 1 1 auto;
  place-items: center;
  overflow: hidden;
}

.lightbox-image-frame {
  position: relative;
  width: fit-content;
  max-width: 100%;
  max-height: min(72vh, 760px);
  line-height: 0;
  transform-origin: center;
  transition: transform 140ms ease;
  cursor: zoom-in;
  touch-action: none;
  user-select: none;
}

.lightbox-image-frame.zoomed {
  cursor: grab;
}

.lightbox-image-frame.dragging {
  cursor: grabbing;
  transition: none;
}

.lightbox-image-frame > img:first-child,
.lightbox-binary-mask {
  display: block;
  width: auto;
  max-width: min(90vw, 1440px);
  max-height: min(72vh, 760px);
  border-radius: 10px;
  object-fit: contain;
  box-shadow: 0 22px 68px rgb(0 0 0 / 58%), 0 0 0 1px rgb(255 255 255 / 14%);
}

.lightbox-mask-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.lightbox-binary-mask {
  background: #000;
}

.lightbox-hint {
  margin: 0;
  text-align: center;
}

.interpretation-section.general-results {
  padding-bottom: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 78px;
  padding: 12px;
  border: 1px solid #dce8f0;
  border-radius: 11px;
  background: #fff;
}

.summary-icon {
  flex-basis: 40px;
  width: 40px;
  height: 40px;
}

.summary-card small,
.summary-card strong {
  display: block;
}

.summary-card small {
  margin-bottom: 3px;
  color: var(--muted);
  font-size: 11px;
}

.summary-card strong {
  color: var(--navy);
  font-size: 19px;
}

.positive-summary .summary-icon {
  background: #e3f8ee;
  color: #159262;
  font-size: 22px;
  font-weight: 700;
}

/* Tabla panorámica que lleva al modo individual de la fila elegida. */
.results-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 11px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.results-table th {
  padding: 13px 14px;
  background: var(--navy);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.results-table th:first-child {
  border-radius: 10px 0 0;
}

.results-table th:last-child {
  border-radius: 0 10px 0 0;
}

.results-table td {
  padding: 10px 14px;
  border-top: 1px solid #e7edf2;
  color: var(--ink);
  font-size: 12px;
  vertical-align: middle;
}

.table-image-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 365px;
}

.table-image-name {
  display: block;
  flex: 0 0 130px;
  min-width: 0;
}

.table-image-name strong,
.table-image-name small {
  display: block;
}

.table-image-name strong {
  overflow: hidden;
  color: var(--navy);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-image-name small {
  margin-top: 3px;
  color: var(--muted);
  font-size: 10px;
}

.table-image-pair {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-image-pair > img {
  display: block;
  flex: 0 0 99px;
  width: 99px;
  height: 72px;
  overflow: hidden;
  border-radius: 7px;
  background: #eef2f5;
}

.table-image-pair > img {
  object-fit: cover;
}

.table-image-pair > .table-image-composite {
  flex: 0 0 99px;
  width: 99px;
  height: 72px;
  border-radius: 7px;
  background: #eef2f5;
}

.table-image-composite .general-roi-frame {
  border-width: 1px;
  border-radius: 2px;
}

.table-image-composite .general-roi-frame small {
  top: -10px;
  left: -1px;
  padding: 1px 3px;
  font-size: 5px;
}

.table-image-pair > img.table-mask-image {
  border: 1px solid #657687;
  background: #05090d;
  object-fit: contain;
}

.classification-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 9px;
  border-radius: 18px;
  background: #e8f5ff;
  color: #075b97;
  font-weight: 600;
  white-space: nowrap;
}

.classification-chip.neutral {
  background: #eff3f6;
  color: #566b7b;
}

.classification-chip svg {
  width: 16px;
  height: 16px;
}

.table-confidence {
  display: grid;
  min-width: 105px;
  gap: 5px;
}

.table-confidence > strong {
  color: var(--navy);
  font-size: 14px;
}

.table-confidence .confidence-track {
  height: 6px;
}

.detection-status.clear {
  background: #eef2f5;
  color: #5c6c79;
}

.row-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 9px;
  border: 1px solid #a8cee9;
  border-radius: 7px;
  background: #fff;
  color: #075b97;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}

.row-action:hover {
  background: #eef8ff;
}

.row-action svg {
  width: 14px;
  height: 14px;
}

/* Acciones y aviso final compartidos por ambos modos. */
.results-actions {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 2px;
}

.results-actions .button {
  font-size: 14px;
}

.results-page > .disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-top: 20px;
  font-size: 12px;
}

.results-page > .disclaimer svg {
  flex: 0 0 auto;
  width: 17px;
  height: 17px;
  color: var(--brand);
}

/* Mensaje claro cuando no se dispone de una interpretación en memoria. */
.empty-state {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 42px 22px;
  text-align: center;
}

.empty-state > svg {
  width: 42px;
  height: 42px;
  color: var(--brand);
}

.empty-state h2 {
  margin: 15px 0 6px;
  color: var(--navy);
  font-size: 20px;
}

.empty-state p {
  margin: 0 0 18px;
  color: var(--muted);
  font-size: 14px;
}

.empty-state .button {
  font-size: 14px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

@media (max-width: 1200px) {
  .view-selector {
    width: 250px;
  }

  .view-tab {
    gap: 5px;
    padding-inline: 6px;
    font-size: 12px;
  }

  .current-image-meta {
    gap: 5px;
    font-size: 11px;
  }

  .current-image-meta strong {
    max-width: 115px;
    font-size: 12px;
  }
}

@media (max-width: 950px) {
  .view-selector {
    width: 230px;
  }

  .current-image-meta strong {
    max-width: 95px;
  }
}
@media (max-width: 1000px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .image-navigation {
    grid-template-columns: 1fr 1fr;
  }

  .thumbnails {
    grid-row: 1;
    grid-column: 1 / -1;
  }
}

@media (max-width: 850px) {
  .results-page {
    display: block;
    padding-top: 22px;
  }

  .results-heading {
    margin-bottom: 12px;
  }

  .view-selector {
    top: 70px;
    width: min(100%, 350px);
  }

  .individual-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .results-heading h1 {
    font-size: 27px;
  }

  .results-heading .subhead {
    font-size: 14px;
  }

  .result-visual-heading {
    align-items: stretch;
    flex-direction: column;
    gap: 8px;
  }

  .view-selector {
    width: 100%;
  }

  .current-image-meta {
    align-self: flex-end;
  }

  .view-tab {
    gap: 7px;
    min-height: 45px;
    padding-inline: 8px;
    font-size: 13px;
  }

  .image-section,
  .interpretation-section {
    padding: 15px;
    border-radius: 12px;
  }

  .image-lightbox {
    padding: 15px;
  }

  .lightbox-content {
    min-height: calc(100vh - 30px);
    min-height: calc(100dvh - 30px);
    gap: 12px;
  }

  .lightbox-image-frame {
    max-height: 65vh;
    max-height: 65dvh;
  }

  .lightbox-image-frame > img:first-child,
  .lightbox-binary-mask {
    max-height: 65vh;
    max-height: 65dvh;
  }

  .section-heading {
    align-items: flex-start;
  }

  .image-count {
    font-size: 11px;
  }

  .image-stage {
    min-height: 240px;
    padding: 8px;
  }

  .image-frame > img {
    max-height: 48vh;
  }

  .image-navigation {
    gap: 8px;
  }

  .navigation-button {
    padding-inline: 10px;
    font-size: 11px;
  }

  .thumbnail {
    flex-basis: 58px;
    width: 58px;
    height: 52px;
  }

  .individual-metrics {
    grid-template-columns: 1fr;
  }

  .results-actions {
    justify-content: stretch;
  }

  .results-actions .button {
    flex: 1 1 100%;
  }
}

@media (max-width: 480px) {
  .results-heading .eyebrow {
    font-size: 9px;
  }

  .section-heading h2 {
    font-size: 18px;
  }

  .section-heading {
    flex-direction: column;
    gap: 8px;
  }

  .current-image-meta {
    align-self: flex-start;
    justify-content: flex-start;
    white-space: normal;
  }

  .current-image-meta strong {
    max-width: 58vw;
  }

  .image-navigation {
    grid-template-columns: 1fr 1fr;
  }

  .navigation-button {
    width: 100%;
  }

  .thumbnails {
    justify-content: flex-start;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .experimental-label {
    white-space: normal;
  }

  .roi-row {
    grid-template-columns: 65px minmax(45px, 1fr) 48px;
    gap: 8px;
  }
}
</style>
