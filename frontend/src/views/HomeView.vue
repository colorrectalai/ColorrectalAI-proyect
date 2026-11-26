<template>
  <main class="page public-home">
    <!-- Presentación pública: explica el propósito y ofrece acceso o registro. -->
    <section class="home-hero">
      <!-- Imagen decorativa a altura completa; el contenido permanece encima. -->
      <img class="home-hero-image" src="/img/Fondo2.png" alt="" aria-hidden="true" />
      <div class="home-hero-inner">
      <!-- Texto principal y botones para entrar o crear una cuenta. -->
        <div class="home-copy">
          <h1>Explora imágenes de colonoscopia con una <span class="perspectiva">nueva perspectiva.</span></h1>
          <p>Una plataforma académica para revisar imágenes, visualizar regiones de interés y consultar resultados experimentales.</p>
          <div class="hero-actions">
            <RouterLink class="button" to="/registro">Iniciar interpretacion <ArrowRight /></RouterLink>
            <RouterLink class="hero-secondary" to="/#acerca">Conocer el proyecto<ArrowDown /></RouterLink>
          </div>
          <ul class="hero-features" aria-label="Características de ColorrectalAI">
            <li class="hero-feature">
              <span class="hero-feature-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <path d="m3 9 9-5 9 5-9 5-9-5Z" />
                  <path d="M7 11.2v4.1c3.1 2 6.9 2 10 0v-4.1M21 9v5" />
                </svg>
              </span>
              <span>Enfoque<br />académico</span>
            </li>
            <li class="hero-feature">
              <span class="hero-feature-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <path d="M12 4a3 3 0 0 0-5.8 1.1A3.6 3.6 0 0 0 5 12a3.5 3.5 0 0 0 1 5.9A3.5 3.5 0 0 0 12 20V4Z" />
                  <path d="M12 8h2m-2 4h3m-3 4h2" />
                  <circle cx="17" cy="8" r="1.5" />
                  <circle cx="18" cy="12" r="1.5" />
                  <circle cx="17" cy="16" r="1.5" />
                </svg>
              </span>
              <span>Basado en<br />inteligencia artificial</span>
            </li>
            <li class="hero-feature">
              <span class="hero-feature-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <circle cx="9" cy="13" r="3.2" />
                  <path d="M9 7.8v1.4m0 7.6v1.4m5.2-5.2h-1.4m-7.6 0H3.8m1.5-3.7 1 1m5.4 5.4 1 1m0-7.4-1 1m-5.4 5.4-1 1" />
                  <circle cx="17.5" cy="7" r="2" />
                  <path d="M17.5 3.8v1m0 4.4v1m3.2-3.2h-1m-4.4 0h-1" />
                </svg>
              </span>
              <span>Herramienta<br />de apoyo</span>
            </li>
          </ul>
          <p class="hero-note"><span class="note-marker"></span>Prototipo académico · No brinda diagnósticos médicos</p>
        </div>
      </div>
    </section>

    <!-- Información general sobre el cáncer colorrectal y síntomas frecuentes. -->
    <section class="public-band cancer-section" aria-labelledby="cancer-title">
      <div class="cancer-inner">
        <div class="cancer-copy">
          <h2 id="cancer-title">Conociendo el cáncer colorrectal</h2>
          <p>El cáncer colorrectal es el tercer tipo de cáncer más común y la segunda causa de muerte relacionada con cáncer en el mundo. Afecta el colon o el recto y es más frecuente después de los 50 años, aunque también puede presentarse en personas más jóvenes. La detección temprana mejora las posibilidades de tratamiento.</p>
          <h3>Síntomas habituales</h3>
          <ul class="symptom-list">
            <li v-for="symptom in symptoms" :key="symptom">{{ symptom }}</li>
          </ul>
          <p class="symptom-note">En etapas iniciales puede no haber síntomas. Estas señales también pueden deberse a otras causas; consulta con un profesional de salud.</p>
          <a class=" hero-secondary more-info-link" href="https://www.who.int/news-room/fact-sheets/detail/colorectal-cancer" target="_blank" rel="noopener noreferrer">Más información <span aria-hidden="true">→</span></a>
        </div>

        <img class="cancer-image" src="https://magazine.medlineplus.gov/images/uploads/main_images/ColorectalCancer.jpg" alt="Imagen informativa sobre el cáncer colorrectal, publicada por MedlinePlus Magazine" loading="lazy" />
      </div>
    </section>

    <!-- Presentación breve del propósito y la tecnología del proyecto. -->
    <section class="public-band project-band" id="acerca" aria-labelledby="project-title">
      <img class="big-logo" src="/img/LogoColorrectalAI.png" alt="logo del proyecto" />
      <div class="project-inner">
        <div class="project-copy">
          <h2 id="project-title">¿Qué es ColorrectalAI?</h2>
          <p>ColorrectalAI es una herramienta académica experimental de asistencia analítica que utiliza un modelo de inteligencia artificial basado en arquitectura YOLO para procesar imágenes de colonoscopia. El sistema busca identificar regiones de interés (ROI), estimar probabilidades asociadas a sus salidas y mostrar métricas experimentales de confianza para facilitar su exploración visual.</p>
        </div>
      </div>
    </section>

    <!-- Recorrido de cuatro etapas para preparar, explorar y documentar un caso. -->
    <section class="public-band exploration-section" aria-labelledby="exploration-title">
      <div class="exploration-inner">
        <div class="exploration-heading">
          <div>
            <h2 id="exploration-title">Un recorrido claro, de principio a fin.</h2>
          </div>
          <p>Cada análisis reúne las imágenes, la configuración y sus salidas para facilitar una revisión comprensible y reproducible.</p>
        </div>
        <div class="exploration-grid">
          <article v-for="step in workflowSteps" :key="step.number" class="exploration-card">
            <div class="step-card-top"><span>{{ step.number }}</span><component :is="step.icon" class="step-symbol" :size="20" :stroke-width="1.8" aria-hidden="true" /></div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- Explicación de qué representan y qué no representan las salidas del modelo. -->
    <section class="public-band limits-band" aria-labelledby="limits-title">
      <div class="limits-inner">
        <div class="limits-intro">
          <h2 id="limits-title">Resultados que se pueden explorar, con límites que se deben conocer.</h2>
          <p>ColorrectalAI conecta visión por computador y aprendizaje automático con imágenes de endoscopia de conjuntos públicos, anonimizadas y desidentificadas.</p>
        </div>
        <div class="limits-list">
          <article v-for="limit in resultLimits" :key="limit.title" class="limit-item">
            <h3>{{ limit.title }}</h3>
            <p>{{ limit.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- Invitación para iniciar el flujo y aviso visible sobre el uso experimental. -->
    <section class="public-band start-band" aria-labelledby="start-title">
      <div class="start-inner">
        <div class="start-heading">
          <div>
            <h2 id="start-title">Empieza por un ejemplo. Conserva el contexto.</h2>
            <p>Crea una cuenta para organizar tus análisis, comparar imágenes y recuperar la configuración de cada interpretación.</p>
          </div>
          <RouterLink class="button " to="/registro"> Crear cuenta académica <ArrowRight /></RouterLink>
        </div>
        <p class="academic-notice"><span aria-hidden="true">ⓘ</span> Resultados experimentales para investigación y educación. No constituyen un diagnóstico, no sustituyen el criterio médico profesional ni ofrecen recomendaciones de tratamiento.</p>
      </div>
    </section>

    <!-- Pie de página con identidad y carácter académico del proyecto. -->
    <footer class="public-band public-footer">
      <div class="footer-inner">
        <BrandLogo compact />
        <p>Proyecto académico · Investigación y educación</p>
      </div>
    </footer>
  </main>
</template>

<script setup>
// Reutiliza la marca compartida y mantiene en datos los textos repetidos de estas secciones.
import { onMounted, onUnmounted } from 'vue'
import BrandLogo from '../components/BrandLogo.vue'
import { ArrowRight, ArrowDown } from '@lucide/vue'
import { workflowSteps } from '../data/workflowSteps'

let sectionRevealObserver

onMounted(() => {
  const sections = document.querySelectorAll('.public-home > section, .public-home > footer')
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  if (reduceMotion || !('IntersectionObserver' in window)) return

  sectionRevealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('is-visible')
      sectionRevealObserver.unobserve(entry.target)
    })
  }, { threshold: 0.12, rootMargin: '0px 0px -36px 0px' })

  sections.forEach((section) => {
    section.classList.add('scroll-reveal')
    sectionRevealObserver.observe(section)
  })
})

onUnmounted(() => sectionRevealObserver?.disconnect())

// Señales descritas por la OMS; no son específicas y pueden tener otras causas.
const symptoms = [
  'Cambios persistentes en el ritmo intestinal.',
  'Presencia de sangre en las heces o sangrado rectal.',
  'Dolor, cólicos o hinchazón abdominal frecuente.',
  'Cansancio extremo o anemia inexplicable.',
  'Pérdida de peso sin motivo aparente.',
]

// Límites de interpretación de las salidas experimentales.
const resultLimits = [
  { title: 'Región de interés (ROI)', description: 'Es una zona delimitada por el modelo para su exploración visual. Su presencia o ausencia no confirma ni descarta una enfermedad.' },
  { title: 'Clasificación experimental', description: 'Es una etiqueta de salida del modelo, no una conclusión médica. Puede contener errores y debe revisarse con su contexto.' },
  { title: 'Confianza del modelo', description: 'Es la puntuación asignada a una salida. No equivale a probabilidad de enfermedad, precisión validada ni certeza clínica.' },
]
</script>

<style scoped>
/* Distribución del mensaje principal y su previsualización de producto. */

.public-home > .scroll-reveal {
  opacity: 0;
  transform: translateY(22px);
  transition: opacity .65s ease, transform .65s cubic-bezier(.2, .65, .3, 1);
}

.public-home > .scroll-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .public-home > .scroll-reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

.home-hero {
  position: relative;
  display: block;
  width: 100%;
  overflow: hidden;
  isolation: isolate;
  border-bottom: 1px solid #f5f6f6;
  background: #ffff;
}

.home-hero-image {
  position: absolute;
  right: 0;
  z-index: 0;
  width: auto;
  height: 100%;
  object-fit: contain;
  object-position: right center;
  pointer-events: none;
  -webkit-mask-image: linear-gradient(to left, #000 60%, transparent 100%);
  mask-image: linear-gradient(to left, #000 10%, transparent 100%);
}
.perspectiva {
  color:var(--blue);
}
.home-copy {
  width: 680px;
  height: auto;
  padding: 20px 0 0 50px;
}
.home-copy h1 {
  margin:0 0 17px;
  color:var(--navy);
  font-size:60px;
  line-height:1.08;
  letter-spacing:-1.8px;
}
.home-copy > p:not(.hero-note) {
  margin:0;
  color:var(--navy);
  font-size:17px;
  line-height:1.7;
}
.hero-actions {
  display:flex;
  align-items:center;
  gap:22px;
  margin-top:26px;
}
.hero-features {
  display: flex;
  align-items: center;
  gap: clamp(16px, 2.8vw, 28px);
  margin: 23px 0 0;
  padding: 0;
  list-style: none;
}

.hero-feature {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--navy);
  font-size: 13px;
  line-height: 1.3;
}

.hero-feature-icon {
  display: grid;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  background: #d7f1ff;
  color: var(--blue);
}

.hero-feature-icon svg {
  width: 23px;
  height: 23px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.hero-secondary {
  color:var(--blue);
  font-size:16px;
  font-weight:700;
  text-decoration:none;
  min-height: 42px;
  padding: 0 17px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--brand);
  border-radius: 15px;
  line-height: 1.2;
  cursor: pointer;
  transition: background .15s ease, transform .15s ease, box-shadow .15s ease;
}
.hero-secondary:hover {
  color: #fff;
  background: #27bafa;
  border-color: #27bafa;
  box-shadow: 0 4px 12px #12476622;
  transform: translateY(-1px);
}
.note-marker {
  width:7px;
  height:7px;
  border-radius:50%;
  background:var(--teal);
}
/* Tarjeta de muestra de una interpretación experimental. */
/* Presentación de los pasos de uso y del aviso del pie de página. */
.public-footer p {
  max-width:610px;
  margin:0;
  color:var(--quiet);
  font-size:9px;
  line-height:1.6;
  text-align:right;
}
/* En tablet y móvil, la presentación pasa de columnas a una sola columna. */
@media (max-width:900px) {

  .home-copy {
    max-width:680px;
  }
  .home-copy h1 {
    max-width:620px;
    font-size:clamp(35px,6vw,48px);
  }
}
@media (max-width:620px) {
  .public-home {
    padding-top:18px;
  }

  .home-copy h1 {
    font-size:36px;
    letter-spacing:-1.2px;
  }
  .home-copy > p:not(.hero-note) {
    font-size:13px;
  }
  .hero-actions {
    align-items:flex-start;
    gap:14px;
    flex-direction:column;
  }
.public-footer {
    align-items:flex-start;
    flex-direction:column;
    gap:12px;
  }
  .public-footer p {
    text-align:left;
  }
}

/* Secciones informativas completas del inicio público. */

.cancer-section,
.exploration-section {
  background: var(--canvas);
  border-top: 2px solid #dce9f2;
}
.cancer-inner,
.exploration-inner,
.limits-inner,
.start-inner,
.footer-inner {
  width: min(100%, 1296px);
  margin: 0 auto;
}
.cancer-inner {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(300px, .92fr);
  align-items: center;
  gap: clamp(32px, 6vw, 86px);
  padding: 48px 0 52px;
}
.cancer-copy {
  padding-left: 60px;
}
.cancer-image {
  display: block;
  width: 80%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  object-position: center;
  border-radius: 12px;
  margin-left: 70px;
}

.section-eyebrow {
  margin: 0 0 9px;
  color: var(--blue);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .7px;
}
.cancer-copy h2,
.project-copy h2,
.exploration-heading h2,
.limits-intro h2,
.start-heading h2 {
  margin: 0;
  color: var(--navy);
  font-size: 35px;
  font-weight: 700;
  line-height: 1.22;
  letter-spacing: -.5px;
}
.more-info-link:hover {
  text-decoration: underline;
}
.project-band,
.limits-band,
.public-footer {
  background: var(--navy);
  color: #fff;
}
.project-band {
  scroll-margin-top: 96px;
  height: 400px;
  position: relative;   /* Referencia para atrapar al pseudoelemento */
  isolation: isolate;   /* Evita que el fondo se esconda detrás del body */
  overflow: hidden;     /* Recorta los bordes blancos que deja el desenfoque */
}

.project-band:before {
  content: "";          /* Obligatorio para que el pseudoelemento exista */
  position: absolute;   /* Flota libremente detrás del contenido */
  inset: 0;             /* Atajo moderno para top: 0, right: 0, bottom: 0, left: 0 */
  z-index: -1;          /* Envía esta capa al fondo */
  background: url('/img/FondoTecnologico2.png') center / cover no-repeat;
  filter: blur(1px);
  opacity: 0.3;
}
.project-inner {
  display: flex;             /* 👈 Activa align-items y justify-content */
  flex-direction: column;    /* 👈 Mantiene los textos uno debajo del otro */
  justify-content: center;   /* 👈 Centra el contenido de arriba a abajo */
  align-items: flex-start;   /* 👈 Mantiene el texto alineado a la izquierda (usa 'center' si lo quieres centrado) */

  width: 500px;
  height: 100%;
  margin-left: 720px;
}

.big-logo {
  position: absolute;
  height: 300px;
  margin-top: 50px;
  margin-left: 200px;
}
.project-brand-panel :deep(.brand-emblem) {
  width: 56px;
  height: 56px;
}
.project-brand-panel :deep(.brand-name) {
  font-size: 21px;
}
.project-brand-panel :deep(.brand-lockup small) {
  font-size: 6px;
}
.project-copy .section-eyebrow,
.limits-band .section-eyebrow {
  color: #48d3ed;
}
.project-copy h2 {
  color: #fff;
}
.exploration-inner {
  padding: 43px 0 50px;
}
.exploration-heading {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: end;
  gap: 28px;
  margin-bottom: 20px;
}
.exploration-heading h2 {
  font-size: clamp(23px, 2.4vw, 30px);
}
.exploration-grid {
  height: 180px;
  padding: 20px 0 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.exploration-card {
  min-height: 132px;
  padding: 14px 13px;
  border: 1px solid #cfe0f1;
  border-radius: 8px;
  background: #fbfdff;
}
.step-symbol {
  flex: 0 0 auto;
  width: 30px;
  height: auto;
  stroke-width: 1.8;
}
.limits-inner {
  display: grid;
  grid-template-columns: minmax(0, .72fr) minmax(0, 1.28fr);
  align-items: start;
  gap: clamp(34px, 7vw, 95px);
  padding: 42px 0 45px;
}
.limits-intro {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 12px;
}
.limits-intro h2 {
  max-width: 420px;
  color: #fff;
  font-size: clamp(24px, 2.8vw, 32px);
}
.limits-intro > p:last-child {
  max-width: 420px;
  margin: 16px 0 0;
  color: #c4d4e5;
  font-size: 15px;
  line-height: 1.65;
}
.limits-list {
  display: grid;
}
.limit-item {
  padding: 3px 0 14px;
  border-bottom: 1px solid #ffffff23;
  padding-top: 13px;
}

.limit-item p {
  margin: 0;
  color: #c4d4e5;
  font-size: 15px;
  line-height: 1.55;
}
.start-band {
  background: #eff9ff;
}
.start-inner {
  padding: 31px 0 28px;
}
.start-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 25px;
}
.start-heading h2 {
  font-size: clamp(20px, 2.2vw, 26px);
}
.academic-notice span {
  flex: 0 0 auto;
  font-size: 13px;
}
.public-footer {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:25px;
  padding:19px 0 0;
  border-top:1px solid var(--line);
  padding-top: 0;
  padding-bottom: 0;
}
.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 68px;
}
.public-footer :deep(.brand-name) {
  color: #fff;
}
.public-footer :deep(.brand-lockup small) {
  color: #b8c9dc;
}
@media (max-width: 850px) {

  .cancer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
  .project-inner, .limits-inner { gap: 28px; }
  .exploration-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 620px) {

  .cancer-inner, .project-inner, .limits-inner { grid-template-columns: 1fr; }
  .cancer-inner { gap: 24px; padding: 32px 0; }
  .project-inner { gap: 22px; padding: 28px 0; }
  .project-band { scroll-margin-top: 120px; }
  .project-brand-panel { min-height: 125px; }
  .exploration-inner { padding: 32px 0 36px; }
  .exploration-heading { grid-template-columns: 1fr; gap: 8px; }
  .exploration-heading > p { justify-self: start; }
  .exploration-grid { grid-template-columns: 1fr 1fr; gap: 8px; }
  .exploration-card { min-height: 150px; padding: 12px 10px; }
  .limits-inner { gap: 24px; padding: 32px 0 35px; }
  .start-heading { align-items: flex-start; flex-direction: column; }
.footer-inner { align-items: flex-start; flex-direction: column; justify-content: center; padding: 17px 0; }
}



/* Jerarquía y ejes compartidos por la presentación y el bloque informativo. */
.hero-note {
  display:flex;
  align-items:center;
  gap:8px;
  margin:23px 0 0;
  color:var(--quiet);
  font-size: 11px;
}
.cancer-copy > p:not(.section-eyebrow):not(.symptom-note) {
  max-width: 650px;
  margin: 12px 0 16px;
  color: #334e70;
  font-size: 17px;
  line-height: 1.65;
}
.cancer-copy h3 {
  margin: 16px 0 6px;
  color: var(--navy);
  font-size: 20px;
}
.symptom-list {
  display: grid;
  margin: 15px 0;
  padding-left: 17px;
  color: #334e70;
  gap: 5px;
  font-size: 17px;
  line-height: 1.5;
}
.symptom-note {
  margin: 10px 0 8px;
  color: var(--muted);
  line-height: 1.5;
  font-size: 11px;
}
.more-info-link {
  display: inline-flex;
  margin-top: 12px;
  align-items: center;
  gap: 9px;
  color: var(--blue);
  font-weight: 700;
  text-decoration: none;
  font-size: 12px;
}
.project-copy > p:last-child {
  max-width: 720px;
  margin: 13px 0 0;
  color: #d5e2f0;
  line-height: 1.65;
  font-size: 17px;
}
.exploration-heading > p {
  max-width: 500px;
  justify-self: end;
  margin: 0 0 3px;
  color: var(--muted);
  line-height: 1.6;
  font-size: 12px;
}
.step-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 13px;
  color: var(--blue);
  font-weight: 700;
  font-size: 20px;
}
.exploration-card h3 {
  margin: 0 0 8px;
  color: #18365f;
  font-weight: 500;
  font-size: 18px;
}
.exploration-card > p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
}
.limit-item h3 {
  margin: 0 0 6px;
  color: #fff;
  font-weight: 600;
  font-size: 18px;
}
.start-heading p {
  max-width: 720px;
  margin: 7px 0 0;
  color: var(--muted);
  line-height: 1.55;
  font-size: 12px;
}
.academic-notice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 18px 0 0;
  padding: 11px 13px;
  border-radius: 5px;
  background: #d9f1ff;
  color: #294a67;
  line-height: 1.5;
  font-size: 11px;
}
.footer-inner p {
  margin: 0;
  color: #b8c9dc;
  font-size: 10px;
}
@media (max-width: 850px) {
  .public-home { --home-gutter: 24px; }

}
@media (max-width: 620px) {

  .cancer-copy > p:not(.section-eyebrow):not(.symptom-note) { font-size: 15px; }
  .symptom-list { font-size: 14px; }
  .exploration-card h3 { font-size: 15px; }
}


/* Los fondos ocupan el ancho completo; el contenido usa un mismo eje centrado. */
.public-home {
  --home-gutter: clamp(28px, 5vw, 72px);
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
  background: #fff;
}

.home-hero-inner,
.cancer-inner,
.exploration-inner,
.limits-inner,
.start-inner,
.footer-inner {
  width: min(1296px, calc(100% - var(--home-gutter) - var(--home-gutter)));
  margin-inline: auto;
}
.home-hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, .88fr) minmax(0, 1.12fr);
  align-items: center;
  gap: clamp(34px, 5vw, 72px);
  padding: 46px 0 58px;
}
.public-band {
  width: 100%;
  margin: 0;
  padding: 0;
}
@media (max-width: 900px) {
  .public-home { --home-gutter: 24px; }
  .home-hero-inner {
    grid-template-columns: 1fr;
    gap: 30px;
    padding: 34px 0 46px;
  }
}
@media (max-width: 620px) {
  .public-home { --home-gutter: 15px; }

}

@media (max-width: 620px) {
  .hero-features {
    flex-wrap: wrap;
    gap: 12px 18px;
    margin-top: 19px;
  }

  .hero-feature {
    font-size: 11px;
  }

  .hero-feature-icon {
    flex-basis: 36px;
    width: 36px;
    height: 36px;
  }
}
</style>
