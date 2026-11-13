<script setup>
import { useRouter } from 'vue-router'
import { estado } from '../store'

const router = useRouter()

// Añade las imágenes elegidas (sin repetir) y guarda los archivos para enviarlos a la API.
const pick = (event) => {
  const nuevas = [...event.target.files].filter(
    (f) => f.type.startsWith('image/') && !estado.archivos.some((a) => a.name === f.name && a.size === f.size),
  )
  estado.archivos = [...estado.archivos, ...nuevas].slice(0, 10)
  event.target.value = ''
}
const quitar = (i) => estado.archivos.splice(i, 1)
const iniciar = () => router.push('/analizando')
</script>

<template>
  <main class="page">
    <!-- Encabezado con el objetivo de la pantalla de carga. -->
    <p class="eyebrow">NUEVA INTERPRETACIÓN / CARGA</p>
    <h1>Carga de imágenes de endoscopia</h1>
    <p class="subhead">Selecciona una o varias imágenes para crear una interpretación académica.</p>

    <section class="upload-layout">
      <!-- Área de carga, lista de archivos y botón para continuar el flujo. -->
      <div class="panel upload-panel">
        <label class="dropzone">
          <span class="upload-icon">↑</span>
          <b>Arrastra las imágenes aquí</b>
          <small>o selecciona archivos desde tu equipo</small>
          <span class="button">
            Seleccionar imágenes
            <input type="file" accept="image/*" multiple hidden @change="pick" />
          </span>
          <small>Formatos admitidos: JPG o PNG</small>
        </label>

        <!-- Solo aparece después de seleccionar al menos un archivo. -->
        <div v-if="estado.archivos.length" class="file-list">
          <p v-for="(file, i) in estado.archivos" :key="file.name + file.size">
            {{ file.name }}
            <span>{{ (file.size / 1024).toFixed(0) }} KB　<a class="quitar" href="#" @click.prevent="quitar(i)">Quitar</a></span>
          </p>
        </div>

        <div class="upload-actions">
          <span>▧　Formato JPG o PNG</span>
          <button class="button" :disabled="!estado.archivos.length" @click="iniciar">Iniciar análisis →</button>
        </div>
      </div>

      <!-- Consejos de preparación que acompañan al selector de archivos. -->
      <aside class="panel tips">
        <h2>Antes de comenzar</h2>
        <p>Calidad de imagen<br /><small>Imágenes nítidas y bien iluminadas</small></p>
        <p>Múltiples imágenes<br /><small>Puedes agregar varias imágenes</small></p>
        <p>Formato compatible<br /><small>JPG o PNG</small></p>
        <p>Calidad de imagen<br /><small>Imágenes nítidas y bien iluminadas</small></p>
      </aside>
    </section>

    <!-- Recordatorio para no cargar datos personales de pacientes. -->
    <p class="disclaimer">ⓘ　No cargues datos identificables de pacientes. Esta herramienta es experimental y no brinda diagnósticos médicos.</p>
  </main>
</template>
<style scoped>
/* Columnas para el selector de imágenes y el panel de recomendaciones. */
.upload-layout {
  display:grid;
  grid-template-columns:minmax(0,1fr) 280px;
  gap:16px;
  margin-top:25px;
}
.upload-panel,.tips {
  padding:20px;
}
.dropzone {
  min-height:300px;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-direction:column;
  gap:12px;
  border:1px dashed #8dbfd2;
  border-radius:7px;
  background:#f8fcfd;
  color:var(--ink);
  cursor:pointer;
  text-align:center;
  transition:border-color .15s ease,background .15s ease;
}
.dropzone:hover {
  border-color:var(--brand);
  background:#f1fafc;
}
/* El input transparente cubre el botón para abrir el selector del sistema. */
.dropzone > b {
  font-size:13px;
}
.dropzone > small {
  color:var(--muted);
  font-size:10px;
}
.dropzone > .button {
  position:relative;
  margin:3px 0;
}
.dropzone input[type="file"] {
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  opacity:0;
  cursor:pointer;
}
.upload-icon {
  display:grid;
  width:46px;
  height:46px;
  place-items:center;
  border:1px solid #cfe8ef;
  border-radius:50%;
  background:#eaf7fa;
  color:var(--brand);
  font-size:25px;
}
/* Lista de archivos elegidos y acciones del área de carga. */
.file-list {
  margin-top:13px;
  padding:0 10px;
  border:1px solid var(--line);
  border-radius:6px;
}
.file-list p {
  display:flex;
  justify-content:space-between;
  gap:10px;
  margin:0;
  padding:10px 0;
  border-bottom:1px solid #edf1f4;
  color:var(--ink);
  font-size:10px;
}
.file-list p:last-child {
  border-bottom:0;
}
.file-list span {
  color:var(--muted);
  white-space:nowrap;
}
.upload-actions {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-top:17px;
  color:var(--muted);
  font-size:10px;
}
.tips h2 {
  margin:1px 0 11px;
  color:var(--navy);
  font-size:14px;
}
.tips p {
  margin:0;
  padding:13px 0;
  border-bottom:1px solid #edf1f4;
  color:var(--ink);
  font-size:10px;
  font-weight:600;
  line-height:1.6;
}
.tips p:last-child {
  border-bottom:0;
}
.tips small {
  color:var(--muted);
  font-size:9px;
  font-weight:400;
}
/* En pantallas pequeñas, las recomendaciones se acomodan bajo el selector. */
@media (max-width:850px) {
  .upload-layout {
    grid-template-columns:1fr;
  }
  .tips {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    column-gap:18px;
  }
  .tips h2 {
    grid-column:1/-1;
  }
}
@media (max-width:620px) {
  .upload-panel,.tips {
    padding:14px;
  }
  .dropzone {
    min-height:250px;
    padding:18px;
  }
  .upload-actions {
    align-items:flex-start;
    flex-direction:column;
  }
  .tips {
    grid-template-columns:1fr;
  }
  .tips h2 {
    grid-column:auto;
  }
}
.quitar {
  color:var(--brand);
  text-decoration:none;
}
.button:disabled {
  opacity:.45;
  cursor:not-allowed;
}
</style>
