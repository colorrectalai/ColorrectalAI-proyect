<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, CloudUpload, FileImage, Images, Info } from '@lucide/vue'
import { estado } from '../store'

const router = useRouter()
const isDragging = ref(false)

// Cada vez que se entra a la vista se inicia una carga nueva, incluso si se llega desde el historial.
estado.archivos = []

// Incorpora archivos JPG o PNG, evita duplicados y limita cada interpretación a diez imágenes.
const addFiles = (files) => {
  const nuevas = [...files].filter(
    (file) =>
      ['image/jpeg', 'image/png'].includes(file.type) &&
      !estado.archivos.some((actual) => actual.name === file.name && actual.size === file.size),
  )
  estado.archivos = [...estado.archivos, ...nuevas].slice(0, 10)
}

// El selector del sistema y el área de arrastre comparten la misma validación.
const pick = (event) => {
  addFiles(event.target.files)
  event.target.value = ''
}
const dragOver = () => {
  isDragging.value = true
}
const dragLeave = (event) => {
  if (!event.currentTarget.contains(event.relatedTarget)) isDragging.value = false
}
const drop = (event) => {
  isDragging.value = false
  addFiles(event.dataTransfer.files)
}

const quitar = (index) => estado.archivos.splice(index, 1)
const iniciar = () => router.push('/analizando')
</script>

<template>
  <main class="page upload-page">
    <!-- Encabezado que ubica la tarea dentro del flujo de interpretación. -->
    <header class="upload-heading">
      <h1>Carga de imágenes.</h1>
    </header>

    <!-- Panel principal: área de carga a la izquierda y recomendaciones al costado. -->
    <section class="upload-card" aria-label="Carga de imágenes">

      <!-- Consejos presentados por el isotipo de ColorrectalAI. -->
      <aside class="tips-panel" aria-labelledby="tips-title">
        <div class="tips-intro">
          <img src="/img/Logotipo.png" alt="Isotipo de ColorrectalAI" />
          <div class="tips-intro-copy">
            <h2 id="tips-title">Antes de comenzar</h2>
          </div>
        </div>
        <p class="tips-message">Para obtener una revisión más clara, ten en cuenta estas recomendaciones:</p>

        <ul class="tips-list">
          <li>
            <span class="tip-icon"><FileImage aria-hidden="true" /></span>
            <span><strong>Calidad de imagen</strong><small>Elige imágenes nítidas y bien iluminadas.</small></span>
          </li>
          <li>
            <span class="tip-icon"><Images aria-hidden="true" /></span>
            <span><strong>Múltiples imágenes</strong><small>Puedes agregar hasta 10 imágenes por análisis.</small></span>
          </li>
          <li>
            <span class="tip-icon"><Info aria-hidden="true" /></span>
            <span><strong>Formato compatible</strong><small>Usa archivos JPG o PNG.</small></span>
          </li>
        </ul>
        <p class="tips-reminder">Recuerda: esta herramienta es académica y experimental.</p>
      </aside>

      <div class="upload-main">
        <!-- El área admite tanto arrastrar archivos como abrir el selector del equipo. -->
        <div
          class="dropzone"
          :class="{ 'is-dragging': isDragging }"
          @dragover.prevent="dragOver"
          @dragleave.prevent="dragLeave"
          @drop.prevent="drop"
        >
          <div class="image-placeholders" aria-hidden="true">
            <span class="placeholder-card placeholder-card-back"><FileImage /></span>
            <span class="placeholder-card placeholder-card-front"><FileImage /></span>
            <span class="placeholder-upload"><CloudUpload /></span>
          </div>
          <h2>Arrastra las imágenes aquí</h2>
          <p>o selecciona archivos desde tu equipo</p>
          <input
            id="endoscopy-images"
            class="visually-hidden"
            type="file"
            accept="image/jpeg,image/png"
            multiple
            @change="pick"
          />
          <label class="button select-button" for="endoscopy-images">
            <Images aria-hidden="true" />
            Seleccionar imágenes
          </label>
          <small class="format-note">Formatos admitidos: JPG o PNG · Hasta 10 imágenes</small>
        </div>

        <!-- Archivos seleccionados con una acción individual para quitarlos. -->
        <div v-if="estado.archivos.length" class="file-list" aria-live="polite">
          <div class="file-list-heading">
            <h3>Imágenes seleccionadas</h3>
            <span>{{ estado.archivos.length }} / 10</span>
          </div>
          <ul>
            <li v-for="(file, index) in estado.archivos" :key="file.name + file.size">
              <FileImage class="file-icon" aria-hidden="true" />
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ (file.size / 1024).toFixed(0) }} KB</span>
              <button class="remove-file" type="button" @click="quitar(index)">Quitar</button>
            </li>
          </ul>
        </div>

        <!-- Nota de uso responsable y botón para continuar al análisis. -->
        <div class="upload-footer">
          <p class="privacy-note">
            <Info aria-hidden="true" />
            <span>No cargues datos identificables de pacientes. Esta herramienta es experimental y no brinda diagnósticos médicos.</span>
          </p>
          <button class="button analyze-button" :disabled="!estado.archivos.length" @click="iniciar">
            Iniciar análisis <ArrowRight aria-hidden="true" />
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* La vista conserva el lienzo general de la aplicación y deja el encabezado despejado. */
.upload-page {
  max-width: 1440px;
  margin-inline: auto;
  position: relative;   /* Necesario para contener el ::before */
  isolation: isolate;   /* Evita que el z-index: -1 se esconda detrás del body */
}

.upload-page::before {
  content: "";
  position: absolute;
  inset: -20px calc((100% - 100vw) / 2); /* Extiende la capa hasta ambos bordes del viewport */
  z-index: -1;
  pointer-events: none;

  background: url("/img/Fondo4.png") center / cover no-repeat;

  filter: blur(3px);
}

.upload-heading .eyebrow span {
  padding-inline: 4px;
  color: var(--quiet);
}

.upload-heading h1 span {
  color: var(--brand);
}

/* Tarjeta blanca que agrupa la carga y los consejos, como en la referencia. */
.upload-card {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
  margin-top: 30px;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--surface);
  box-shadow: 0 12px 34px rgb(20 55 85 / 7%);
}

.upload-main {
  min-width: 0;
}

/* Zona de arrastre con símbolos de imagen genéricos, nunca fotos médicas. */
.dropzone {
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 28px;
  border: 1.5px dashed #8dcdf0;
  border-radius: 14px;
  background: #f8fcff;
  color: var(--ink);
  text-align: center;
  transition: border-color 160ms ease, background-color 160ms ease, box-shadow 160ms ease;
}

.dropzone:hover,
.dropzone.is-dragging {
  border-color: var(--brand);
  background: #f0f9ff;
  box-shadow: inset 0 0 0 1px rgb(0 157 255 / 10%);
}

.image-placeholders {
  position: relative;
  width: 190px;
  height: 145px;
  margin-bottom: 22px;
}

.placeholder-card {
  position: absolute;
  display: grid;
  place-items: center;
  width: 96px;
  height: 112px;
  border: 1px solid #d4e8f5;
  border-radius: 14px;
  background: linear-gradient(145deg, #fff, #edf7fd);
  color: #78bce6;
  box-shadow: 0 12px 26px rgb(26 94 139 / 10%);
}

.placeholder-card svg {
  width: 36px;
  height: 36px;
  stroke-width: 1.5;
}

.placeholder-card-back {
  top: 15px;
  left: 23px;
  transform: rotate(-12deg);
}

.placeholder-card-front {
  top: 4px;
  right: 22px;
  transform: rotate(9deg);
}

.placeholder-upload {
  position: absolute;
  right: 54px;
  bottom: 0;
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  border: 4px solid #f8fcff;
  border-radius: 50%;
  background: var(--brand);
  color: #fff;
  box-shadow: 0 8px 18px rgb(0 125 220 / 24%);
}

.placeholder-upload svg {
  width: 27px;
  height: 27px;
  stroke-width: 2;
}

.dropzone h2 {
  margin: 0;
  color: var(--navy);
  font-size: clamp(20px, 2vw, 25px);
  font-weight: 700;
  letter-spacing: -0.025em;
}

.dropzone > p {
  margin: 8px 0 18px;
  color: var(--muted);
  font-size: 15px;
}

.select-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 52px;
  padding-inline: 26px;
  cursor: pointer;
}

.select-button svg,
.analyze-button svg {
  width: 19px;
  height: 19px;
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

.visually-hidden:focus-visible + .select-button,
.select-button:focus-visible {
  outline: 3px solid rgb(0 157 255 / 35%);
  outline-offset: 3px;
}

.format-note {
  margin-top: 13px;
  color: var(--muted);
  font-size: 13px;
}

/* Lista compacta para confirmar las imágenes antes de iniciar. */
.file-list {
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
}

.file-list-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 7px;
  color: var(--muted);
  font-size: 13px;
}

.file-list-heading h3 {
  margin: 0;
  color: var(--navy);
  font-size: 14px;
}

.file-list ul,
.tips-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.file-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 9px 0;
  border-top: 1px solid #edf2f6;
  color: var(--ink);
  font-size: 13px;
}

.file-icon {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  color: var(--brand);
}

.file-name {
  overflow: hidden;
  flex: 1;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: var(--muted);
  white-space: nowrap;
}

.remove-file {
  padding: 4px 0 4px 6px;
  border: 0;
  background: transparent;
  color: var(--brand);
  font: inherit;
  cursor: pointer;
}

.remove-file:hover {
  text-decoration: underline;
}

/* Recomendaciones con el isotipo como anfitrión de los consejos. */
.tips-panel {
  align-self: stretch;
  padding: 22px 20px;
  border: 1px solid #deedf8;
  border-radius: 14px;
  background: #f2f9fe;
}

.tips-intro {
  display: flex;
  align-items: center;
  gap: 13px;
  padding-bottom: 16px;
  border-bottom: 1px solid #dcecf7;
}

.tips-intro img {
  flex: 0 0 auto;
  width: 52px;
  height: 52px;
  object-fit: contain;
}

.tips-intro-copy > span {
  color: var(--brand);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.07em;
}

.tips-intro h2 {
  margin: 4px 0 0;
  color: var(--navy);
  font-size: 19px;
  letter-spacing: -0.02em;
}

.tips-message {
  margin: 15px 0 5px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.55;
}

.tips-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #dcecf7;
}

.tips-list li:last-child {
  border-bottom: 0;
}

.tip-icon {
  flex: 0 0 auto;
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 11px;
  background: #e0f2ff;
  color: var(--brand);
}

.tip-icon svg {
  width: 20px;
  height: 20px;
  stroke-width: 1.8;
}

.tips-list strong,
.tips-list small {
  display: block;
}

.tips-list strong {
  margin: 1px 0 4px;
  color: var(--navy);
  font-size: 14px;
}

.tips-list small {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}

.tips-reminder {
  margin: 13px 0 0;
  padding: 11px 12px;
  border-radius: 9px;
  background: #e5f4ff;
  color: #315d7f;
  font-size: 12px;
  line-height: 1.5;
}

/* Pie de la tarjeta: advertencia y acción principal quedan alineadas. */
.upload-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  margin-top: 20px;
}

.privacy-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 690px;
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.privacy-note svg {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  margin-top: 1px;
  color: var(--brand);
}

.analyze-button {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 50px;
  padding-inline: 22px;
}

.analyze-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 980px) {
  .upload-card {
    grid-template-columns: minmax(0, 1fr) 280px;
    gap: 18px;
    padding: 18px;
  }

  .dropzone {
    min-height: 390px;
  }
}

@media (max-width: 780px) {
  .upload-card {
    grid-template-columns: 1fr;
  }

  .tips-panel {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
    column-gap: 24px;
  }

  .tips-intro,
  .tips-message,
  .tips-reminder {
    grid-column: 1;
  }

  .tips-list {
    grid-column: 2;
    grid-row: 1 / span 3;
    align-self: center;
  }
}

@media (max-width: 600px) {
  .upload-card {
    gap: 16px;
    margin-top: 22px;
    padding: 12px;
    border-radius: 14px;
  }

  .dropzone {
    min-height: 340px;
    padding: 22px 14px;
  }

  .dropzone h2 {
    font-size: 20px;
  }

  .dropzone > p {
    font-size: 14px;
  }

  .select-button {
    min-height: 48px;
    padding-inline: 18px;
  }

  .tips-panel {
    display: block;
    padding: 18px 16px;
  }

  .upload-footer {
    align-items: stretch;
    flex-direction: column;
    gap: 15px;
  }

  .analyze-button {
    width: 100%;
  }

  .dropzone { min-height: 300px; }
  .image-placeholders { transform: scale(.84); margin-block: -8px; }
  .file-list li { gap: 8px; }
  .file-name { min-width: 0; overflow-wrap: anywhere; }
  .file-size { white-space: nowrap; }
  .remove-file { min-height: 40px; }
  .tips-intro img { width: 46px; height: 46px; object-fit: contain; }
}

@media (max-width: 400px) {
  .upload-card { padding: 10px; }
  .dropzone { padding-inline: 10px; }
  .dropzone h2 { font-size: 18px; }
  .format-note { font-size: 11px; }
  .tips-list { padding-left: 0; }
}
</style>
