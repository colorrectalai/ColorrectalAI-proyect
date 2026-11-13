<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Activity, ArrowRight, FileImage, ScanSearch, Info } from '@lucide/vue'
import HistoryTable from '../components/HistoryTable.vue'

// Nombre de muestra para el prototipo; si hay un nombre guardado, se usa en el saludo.
const firstName = computed(() => {
  const savedName = localStorage.getItem('colorrectalai-user-name')
  return savedName?.trim().split(/\s+/)[0] || 'Juan'
})

// Interpretaciones de ejemplo que ilustran cómo se verá la actividad reciente.
const recent = [
  { date: '18 oct 2025', time: '10:42 a. m.', id: 'A-DEMO-003', case: 'Colonoscopia · Caso de práctica', count: 3, confidence: '94.2%', label: 'Alta', status: 'Completado', note: '18 oct 2025, 10:43' },
  { date: '17 oct 2025', time: '3:16 p. m.', id: 'A-DEMO-002', case: 'Colonoscopia · Caso de práctica', count: 2, confidence: '91.8%', label: 'Alta', status: 'Completado', note: '17 oct 2025, 3:17' },
]

// Indicadores de demostración con iconos del mismo lenguaje visual de HomeView.
const summary = [
  { label: 'Interpretaciones guardadas', value: '24', detail: 'En tu cuaderno académico', icon: Activity },
  { label: 'Imágenes analizadas', value: '37', detail: 'Entre todos los análisis', icon: FileImage },
  { label: 'Regiones de interés', value: '8', detail: 'Marcadas para revisión', icon: ScanSearch },
]

// Muestra cada bloque al entrar en pantalla y elimina el observador al salir de la vista.
const dashboardRoot = ref(null)
let revealObserver

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return

  const revealTargets = dashboardRoot.value?.querySelectorAll(
    '.dashboard-welcome, .dashboard-stats .stat-card, .activity-section, .disclaimer',
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

    <!-- Resumen rápido de las interpretaciones y las imágenes del espacio. -->
    <section class="stats dashboard-stats" aria-label="Resumen de actividad">
      <article v-for="item in summary" :key="item.label" class="stat-card">
        <span class="stat-icon"><component :is="item.icon" :size="21" :stroke-width="1.8" aria-hidden="true" /></span>
        <div class="stat-content">
          <small>{{ item.label }}</small>
          <b>{{ item.value }}</b>
          <i>{{ item.detail }}</i>
        </div>
      </article>
    </section>

    <!-- Actividad más reciente y enlace al historial completo. -->
    <section class="activity-section" aria-labelledby="activity-title">
      <div class="dashboard-section-head">
        <div>
          <p class="eyebrow">TU CUADERNO</p>
          <h2 id="activity-title">Interpretaciones recientes</h2>
          <p class="section-description">Retoma un análisis o consulta sus detalles.</p>
        </div>
        <RouterLink to="/historial" class="row-link">Ver historial completo <ArrowRight :size="16" aria-hidden="true" /></RouterLink>
      </div>

      <!-- Tabla reutilizada para mantener el mismo formato que el historial. -->
      <div class="panel activity-panel">
        <HistoryTable :items="recent" />
      </div>
    </section>

    <!-- Aviso visible sobre el alcance académico y experimental del proyecto. -->
    <p class="disclaimer"><Info :size="17" aria-hidden="true" /> ColorrectalAI es una herramienta académica experimental. Sus resultados no reemplazan el diagnóstico ni la evaluación de un profesional de salud.</p>
  </main>
</template>

<style scoped>
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

/* Resplandor azul suave detrás del monitor, sin un aro dominante. */
.dashboard-welcome::before {
  position: absolute;
  top: 50%;
  right: -40px;
  z-index: 0;
  width: 720px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 157, 255, .32) 10%, rgba(0, 157, 255, .18) 42%, rgba(0, 157, 255, .06) 66%, transparent 72%);
  content: '';
  transform: translateY(-50%);
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
.welcome-img{
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
/* Métricas con más aire, iconografía consistente y texto legible. */
.dashboard-stats {
  gap: 18px;
  margin: 22px 0 40px;
}

.dashboard-stats .stat-card {
  min-height: 124px;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: start;
  column-gap: 15px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(15, 51, 78, .045);
}

.stat-icon {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 12px;
  background: #e5f5ff;
  color: var(--blue);
}

.dashboard-stats .stat-content small {
  margin: 1px 0 5px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.4;
}

.dashboard-stats .stat-content b {
  color: var(--navy);
  font-size: 27px;
  line-height: 1.15;
}

.dashboard-stats .stat-content i {
  grid-column: auto;
  margin-top: 5px;
  color: var(--quiet);
  font-size: 12px;
  font-style: normal;
}

/* Encabezado de actividad y tabla del cuaderno. */
.dashboard-section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin: 0 0 16px;
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
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(15, 51, 78, .045);
}

/* Aumenta la legibilidad de la tabla solo en este panel. */
.activity-panel :deep(.records th) {
  padding: 14px 15px;
  color: #526b80;
  font-size: 11px;
}

.activity-panel :deep(.records td) {
  padding: 14px 15px;
  font-size: 12px;
}

.activity-panel :deep(.records td small) {
  font-size: 11px;
}

.activity-panel :deep(.row-link) {
  font-size: 12px;
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

  .welcome-img {
    max-width: 54%;
    right: 30px;
  }

  .dashboard-welcome::before {
    right: 6%;
    width: 300px;
  }
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

  .welcome-img {
    max-width: 100%;
    opacity: .22;
    right: 0;
    -webkit-mask-image: linear-gradient(to left, #000 12%, transparent 100%);
    mask-image: linear-gradient(to left, #000 12%, transparent 100%);
  }

  .dashboard-welcome::before {
    right: -70px;
    width: 230px;
  }

  .dashboard-stats {
    grid-template-columns: 1fr;
    gap: 10px;
    margin: 16px 0 32px;
  }

  .dashboard-stats .stat-card {
    min-height: 96px;
    padding: 15px 17px;
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

@media (prefers-reduced-motion: reduce) {
  .dashboard .dashboard-reveal,
  .dashboard .dashboard-reveal.is-visible {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
