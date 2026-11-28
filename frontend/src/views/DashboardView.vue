<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Activity, ArrowRight, FileImage, ScanSearch, Info } from '@lucide/vue'
import InterpretationHistoryTable from '../components/InterpretationHistoryTable.vue'
import { listarInterpretaciones, obtenerInterpretacion, restaurarInterpretacion } from '../history'
import { descargarInformePdf } from '../reports/pdfReport'
import { workflowSteps } from '../data/workflowSteps'

const router = useRouter()
const historyEntries = ref([])
const recent = computed(() => historyEntries.value.slice(0, 3))
const recentLoading = ref(true)
const historyError = ref('')
const descargandoPdfId = ref('')

// Nombre de muestra para el prototipo; si hay un nombre guardado, se usa en el saludo.
const firstName = computed(() => {
  const savedName = localStorage.getItem('colorrectalai-user-name')
  return savedName?.trim().split(/\s+/)[0] || 'Juan'
})

// Los contadores se calculan con todas las interpretaciones guardadas localmente.
const summary = computed(() => {
  const imagenes = historyEntries.value.reduce((total, item) => total + item.resultados.length, 0)
  const regiones = historyEntries.value.reduce(
    (total, item) => total + item.resultados.reduce((suma, resultado) => suma + (resultado.respuesta.rois?.length || 0), 0),
    0,
  )

  return [
    { label: 'Interpretaciones guardadas', value: historyEntries.value.length, detail: 'En tu cuaderno académico', icon: Activity },
    { label: 'Imágenes analizadas', value: imagenes, detail: 'En tus interpretaciones', icon: FileImage },
    { label: 'Regiones de interés', value: regiones, detail: 'Señaladas por el modelo', icon: ScanSearch },
  ]
})

// Muestra cada bloque al entrar en pantalla y elimina el observador al salir de la vista.
const dashboardRoot = ref(null)
let revealObserver

// El bloque de actividad muestra solo las cinco interpretaciones más recientes.
onMounted(async () => {
  try {
    historyEntries.value = await listarInterpretaciones()
  } catch (error) {
    historyError.value = error.message || 'No se pudo cargar el historial local.'
  } finally {
    recentLoading.value = false
  }
})

const openInterpretation = async (item) => {
  try {
    await restaurarInterpretacion(item.id)
    await router.push({ name: 'results', params: { id: item.id } })
  } catch (error) {
    historyError.value = error.message || 'No se pudo abrir esta interpretación.'
  }
}

// El dashboard usa el mismo informe PDF que el historial completo.
const downloadInterpretation = async (item) => {
  if (descargandoPdfId.value) return
  historyError.value = ''
  descargandoPdfId.value = item.id
  try {
    const interpretacion = await obtenerInterpretacion(item.id)
    if (!interpretacion) throw new Error('No se encontró esta interpretación en el historial local.')
    await descargarInformePdf(interpretacion)
  } catch (error) {
    historyError.value = error.message || 'No se pudo generar el informe PDF.'
  } finally {
    descargandoPdfId.value = ''
  }
}

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return

  const revealTargets = dashboardRoot.value?.querySelectorAll(
    '.dashboard-welcome, .dashboard-stats .stat-card, .workflow-card, .activity-section, .disclaimer',
  ) ?? []

  revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('is-visible')
      revealObserver.unobserve(entry.target)
    })
  }, { threshold: 0.12, rootMargin: '0px 0px -28px 0px' })

  revealTargets.forEach((element, index) => {
    element.classList.add('dashboard-reveal')
    element.style.setProperty('--reveal-delay', `${Math.min(index % 3, 2) * 80}ms`)
    revealObserver.observe(element)
  })
})

onUnmounted(() => revealObserver?.disconnect())
</script>

<template>
  <main ref="dashboardRoot" class="page dashboard">
    <!-- Bienvenida personalizada y acceso destacado a una nueva interpretación. -->
    <section class="dashboard-welcome" aria-labelledby="welcome-title">
      <img class="welcome-img" src="/img/Fondo3.png" alt="" aria-hidden="true" />
      <div class="welcome-copy">
        <p class="welcome-eyebrow">TU ESPACIO DE TRABAJO</p>
        <h1 id="welcome-title">Hola, {{ firstName }}.</h1>
        <p class="welcome-prompt">¿Listo para una nueva interpretación?</p>
        <p class="welcome-description">Continúa explorando tus imágenes y conserva cada resultado en tu cuaderno académico.</p>
        <RouterLink class="button welcome-action" to="/carga">Nueva interpretación <ArrowRight :size="18" aria-hidden="true" /></RouterLink>
      </div>
    </section>

    <!-- Guía práctica con los mismos pasos que presenta HomeView. -->
    <section class="workflow-section" aria-labelledby="workflow-title">
      <div class="dashboard-section-head">
        <div>
          <h2 id="workflow-title">Un recorrido claro, de principio a fin.</h2>
          <p class="section-description">Prepara tus imágenes, revisa las salidas y conserva el contexto de cada interpretación.</p>
        </div>
      </div>

      <div class="workflow-grid">
        <article v-for="step in workflowSteps" :key="step.number" class="workflow-card">
          <div class="workflow-card-top">
            <span class="workflow-number">{{ step.number }}</span>
            <span class="workflow-icon"><component :is="step.icon" :size="20" :stroke-width="1.8" aria-hidden="true" /></span>
          </div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </article>
      </div>
    </section>

    <hr class="dashboard-divider" aria-hidden="true" />

    <!-- Resumen e historial forman el bloque de información del espacio de trabajo. -->
    <section class="dashboard-data" aria-label="Resumen e historial">

      <div class="dashboard-section-head">
          <div>
            <h2 id="activity-title">Interpretaciones recientes</h2>
            <p class="section-description">Retoma un análisis o consulta sus detalles.</p>
          </div>
          <RouterLink to="/historial" class="row-link">Ver historial completo <ArrowRight :size="16" aria-hidden="true" /></RouterLink>
        </div>
        
      <!-- Resumen rápido de las interpretaciones y las imágenes del espacio. -->
      <section class="stats dashboard-stats" aria-label="Resumen de actividad">
        <article v-for="item in summary" :key="item.label" class="stat-card">
          <div class="stat-value">
            <span class="stat-icon"><component :is="item.icon" :size="28" :stroke-width="1.8" aria-hidden="true" /></span>
            <b>{{ item.value }}</b>
          </div>
          <div class="stat-content">
            <small>{{ item.label }}</small>
            <i>{{ item.detail }}</i>
          </div>
        </article>
      </section>

      <!-- Actividad más reciente y enlace al historial completo. -->
      <section class="activity-section" aria-labelledby="activity-title">

        <!-- Tabla del historial limitada a las tres interpretaciones más recientes. -->
        <div class="panel activity-panel">
          <p v-if="historyError" class="activity-error" role="alert">{{ historyError }}</p>
          <InterpretationHistoryTable
            :items="recent"
            :loading="recentLoading"
            :downloading-id="descargandoPdfId"
            download-label="Descargar resultados PDF"
            :empty-title="historyError ? 'No se pudo cargar el historial' : 'Aún no hay interpretaciones guardadas'"
            :empty-description="historyError ? 'Comprueba el almacenamiento local e inténtalo de nuevo.' : 'Tus análisis completados aparecerán aquí.'"
            empty-to="/carga"
            @open="openInterpretation"
            @download="downloadInterpretation"
          />
        </div>
      </section>
    </section>

    <!-- Aviso visible sobre el alcance académico y experimental del proyecto. -->
    <p class="disclaimer"><Info :size="17" aria-hidden="true" /> ColorrectalAI es una herramienta académica experimental. Sus resultados no reemplazan el diagnóstico ni la evaluación de un profesional de salud.</p>
  </main>
</template>

<style scoped>
/* Fondo general de la vista, independiente de la tarjeta de bienvenida. */
.dashboard {
  position: relative;
  isolation: isolate;
  min-width: 0;
}

.dashboard::before {
  content: '';
  position: absolute;
  inset: -20px calc((100% - 100vw) / 2);
  z-index: -1;
  pointer-events: none;
  background:
    linear-gradient(
      to bottom,
      rgba(243, 248, 253, .84) 0%,
      rgba(243, 248, 253, .2) 100%
    ),
    url('/img/Fondo4.png') center / cover no-repeat;
  filter: blur(2px);
}
/* Panel de bienvenida: contraste navy y acento azul de la identidad del proyecto. */
.dashboard-welcome {
  position: relative;
  isolation: isolate;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 400px;
  overflow: hidden;
  padding: 34px clamp(26px, 4vw, 54px);
  border-radius: 18px;
  color: #fff;
  background:
    linear-gradient(180deg, #071e3621 0%, #071e3633 42%, #071e36d9 100%),
    url('/img/FondoTecnologico3.png') center / cover no-repeat;
}

/* Ilustración de bienvenida visible únicamente en escritorio. */
.welcome-img {
  position: absolute;
  top: 5%;
  right: 90px;
  z-index: 1;
  width: auto;
  height: 90%;
  object-fit: contain;
  object-position: right center;
  pointer-events: none;
}

.welcome-copy {
  position: relative;
  z-index: 3;
  max-width: 700px;
  margin-left: 45px;
}

.welcome-eyebrow {
  margin: 0 0 13px;
  color: #71d4ff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.15px;
}

.welcome-copy h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(34px, 3.2vw, 44px);
  line-height: 1.12;
  letter-spacing: -1.3px;
}

.welcome-prompt {
  margin: 7px 0 0;
  color: #c9eaff;
  font-size: clamp(20px, 2vw, 26px);
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: -.45px;
}

.welcome-description {
  max-width: 560px;
  margin: 12px 0 21px;
  color: #d5e4ef;
  font-size: 15px;
  line-height: 1.65;
}

.welcome-action {
  min-height: 46px;
  padding: 0 19px;
  border-radius: 12px;
  font-size: 15px;
}
/* Métricas con más aire, iconografía consistente y texto legible. */
.dashboard-stats {
  gap: 18px;
  margin: 0;
}

.dashboard-stats .stat-card {
  min-height: 98px;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  column-gap: 14px;
  padding: 14px 18px;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(15, 51, 78, .045);
}

.stat-value {
  display: grid;
  grid-template-columns: 56px auto;
  min-width: 0;
  align-items: center;
  gap: 9px;
}

.stat-icon {
  display: grid;
  width: 56px;
  height: 66px;
  place-items: center;
  border-radius: 13px;
  background: #e5f5ff;
  color: var(--blue);
}

.dashboard-stats .stat-value b {
  color: var(--navy);
  font-size: 29px;
  line-height: 1;
}

.dashboard-stats .stat-content {
  min-width: 0;
  text-align: left;
  justify-self: start;
}

.dashboard-stats .stat-content small {
  margin: 0 0 4px;
  color: var(--navy-deep);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
}

.dashboard-stats .stat-content i {
  display: block;
  margin-top: 3px;
  color: var(--quiet);
  font-size: 11px;
  line-height: 1.35;
  font-style: normal;
}

/* Recorrido de uso presentado en tarjetas claras dentro del espacio privado. */
.workflow-section {
  margin-bottom: 0;
}

.dashboard-divider {
  height: 1px;
  margin: 34px 0 28px;
  border: 0;
  background: linear-gradient(90deg, transparent, #9fc7df 12%, #9fc7df 88%, transparent);
}

.dashboard-data {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 30px;
  min-width: 0;
  max-width: 100%;
}

.workflow-section .dashboard-section-head {
  margin-top: 40px;
  margin-bottom: 16px;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.workflow-card {
  min-height: 174px;
  padding: 17px 18px;
  border: 1px solid #d6e7f3;
  border-radius: 14px;
  background: rgba(255, 255, 255, .94);
  box-shadow: 0 4px 16px rgba(15, 51, 78, .045);
}

.workflow-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.workflow-number {
  color: var(--blue);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: .6px;
}

.workflow-icon {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 11px;
  background: #e5f5ff;
  color: var(--blue);
}

.workflow-card h3 {
  margin: 0 0 7px;
  color: var(--navy-deep);
  font-size: 15px;
  font-weight: 600;
  line-height: 1.35;
}

.workflow-card p {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.55;
}

/* Encabezado de actividad y tabla del cuaderno. */
.dashboard-section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
}

.dashboard-section-head .eyebrow {
  margin-bottom: 7px;
}

.dashboard-section-head h2 {
  margin: 0;
  color: var(--navy-deep);
  font-size: 25px;
  line-height: 1.25;
  letter-spacing: -.55px;
}

.section-description {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.5;
}

.dashboard-section-head .row-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 0;
  font-size: 14px;
  white-space: nowrap;
}

.activity-panel {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(15, 51, 78, .045);
}

.activity-error {
  margin: 12px 16px 0;
  color: #8d3b2e;
  font-size: 13px;
}

/* Nota de alcance en formato compacto, con icono alineado al texto. */
.disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin: 20px 0 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.6;
}

.disclaimer svg {
  flex: 0 0 auto;
  margin-top: 1px;
  color: var(--blue);
}

/* Animación gradual al entrar en pantalla durante la navegación. */
.dashboard .dashboard-reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity .55s ease, transform .55s cubic-bezier(.2, .65, .3, 1);
  transition-delay: var(--reveal-delay, 0ms);
}

.dashboard .dashboard-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 850px) {
  .dashboard-welcome {
    height: 350px;
  }
  .welcome-img { display: none; }
}

@media (max-width: 620px) {
  .dashboard-welcome {
    height: 340px;
    padding: 27px 23px;
    border-radius: 14px;
  }

  .welcome-copy h1 {
    font-size: 34px;
  }

  .welcome-prompt {
    max-width: 400px;
    font-size: 21px;
  }

  .welcome-description {
    font-size: 14px;
  }

  .dashboard-stats {
    grid-template-columns: 1fr;
    gap: 10px;
    margin: 0;
  }

  .dashboard-stats .stat-card {
    min-height: 84px;
    grid-template-columns: auto minmax(0, 1fr);
    padding: 12px 14px;
  }

  .stat-value {
    grid-template-columns: 50px auto;
    gap: 8px;
  }

  .stat-icon {
    width: 50px;
    height: 56px;
  }

  .stat-value :deep(svg) {
    width: 25px;
    height: 25px;
  }

  .workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .workflow-card {
    min-height: 170px;
    padding: 14px;
  }

  .dashboard-divider {
    margin: 26px 0 22px;
  }

  .dashboard-data {
    gap: 24px;
  }

  .dashboard-section-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 7px;
  }

  .dashboard-section-head h2 {
    font-size: 22px;
  }

  .dashboard-section-head .row-link {
    padding: 4px 0;
  }
}

@media (max-width: 420px) {
  .workflow-grid {
    grid-template-columns: 1fr;
  }

  .workflow-card {
    min-height: 0;
  }
}

@media (max-width: 620px) {
  .dashboard-welcome { min-height: 360px; height: auto; }
  .welcome-copy { position: relative; z-index: 2; max-width: 100%; margin-left: 0; }
  .workflow-card h3 { font-size: 16px; }
  .workflow-card p { font-size: 13px; line-height: 1.5; }
  .dashboard-section-head { width: 100%; min-width: 0; }
  .activity-section, .activity-panel { width: 100%; min-width: 0; max-width: 100%; }
  .activity-panel :deep(.history-table-scroll) { width: 100%; min-width: 0; max-width: 100%; overflow-x: auto; }
}

@media (prefers-reduced-motion: reduce) {
  .dashboard .dashboard-reveal,
  .dashboard .dashboard-reveal.is-visible {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
