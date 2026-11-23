<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { ArrowRight, Download, FileImage } from '@lucide/vue'
import { obtenerMiniatura } from '../history'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  downloadingId: { type: String, default: '' },
  downloadLabel: { type: String, default: 'Descargar resumen JSON' },
  emptyTitle: { type: String, default: 'Todavía no hay interpretaciones guardadas' },
  emptyDescription: { type: String, default: 'Cuando completes un análisis, aparecerá aquí.' },
  emptyTo: { type: String, default: '' },
})

const emit = defineEmits(['open', 'download'])
const miniaturas = ref({})
let cargaMiniaturas = 0

const filas = computed(() => props.items.map((item) => {
  const fecha = new Date(item.createdAt)
  const regiones = item.resultados.reduce((total, resultado) => total + (resultado.respuesta.rois?.length || 0), 0)
  const modelo = item.resultados.find((resultado) => resultado.respuesta.modelo_version)?.respuesta.modelo_version || 'Modelo experimental'
  return { ...item, fecha, regiones, modelo }
}))

const fechaCorta = (valor) => new Intl.DateTimeFormat('es-CO', {
  day: '2-digit', month: 'short', year: 'numeric',
}).format(new Date(valor)).replace('.', '')
const horaCorta = (valor) => new Intl.DateTimeFormat('es-CO', {
  hour: '2-digit', minute: '2-digit', hour12: true,
}).format(new Date(valor))

watch(
  () => props.items.map((item) => item.id).join('|'),
  async () => {
    const cargaActual = ++cargaMiniaturas
    Object.values(miniaturas.value).forEach((url) => URL.revokeObjectURL(url))
    miniaturas.value = {}
    const urls = {}
    await Promise.all(props.items.map(async (item) => {
      try {
        const blob = await obtenerMiniatura(item.id)
        if (blob) urls[item.id] = URL.createObjectURL(blob)
      } catch (error) {
        console.warn(`No se pudo cargar la miniatura de ${item.id}:`, error)
      }
    }))
    if (cargaActual !== cargaMiniaturas) {
      Object.values(urls).forEach((url) => URL.revokeObjectURL(url))
      return
    }
    miniaturas.value = urls
  },
  { immediate: true },
)

onUnmounted(() => {
  cargaMiniaturas++
  Object.values(miniaturas.value).forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <div class="history-table-scroll">
    <table class="history-table">
      <thead>
        <tr>
          <th scope="col">Fecha</th>
          <th scope="col">ID de análisis</th>
          <th scope="col">Imágenes</th>
          <th scope="col">ROI</th>
          <th scope="col">Modelo / umbral</th>
          <th scope="col">Estado</th>
          <th scope="col">Acciones</th>
        </tr>
      </thead>
      <tbody v-if="loading">
        <tr><td colspan="7" class="empty-cell"><strong>Cargando historial...</strong><span>Espera un momento.</span></td></tr>
      </tbody>
      <tbody v-else-if="filas.length">
        <tr v-for="item in filas" :key="item.id">
          <td class="date-cell"><strong>{{ fechaCorta(item.createdAt) }}</strong><small>{{ horaCorta(item.createdAt) }}</small></td>
          <td class="id-cell"><strong>{{ item.id }}</strong><small>Interpretación experimental</small></td>
          <td>
            <div class="image-count-cell">
              <span class="image-stack" aria-hidden="true">
                <span class="stack-card stack-back"></span>
                <span class="stack-card stack-middle"></span>
                <img v-if="miniaturas[item.id]" :src="miniaturas[item.id]" alt="" />
                <span v-else class="stack-placeholder"><FileImage aria-hidden="true" /></span>
              </span>
              <span class="count-pill">{{ item.resultados.length }} {{ item.resultados.length === 1 ? 'archivo' : 'archivos' }}</span>
            </div>
          </td>
          <td><strong class="roi-count">{{ item.regiones }} ROI</strong></td>
          <td class="model-cell"><strong>{{ item.modelo }}</strong><small>Umbral configurado en API</small></td>
          <td>
            <span class="completed-badge"><span aria-hidden="true">✓</span> Completado</span>
            <small class="experimental-note">Experimental</small>
          </td>
          <td>
            <div class="row-actions">
              <button class="open-button" type="button" @click="emit('open', item)">Abrir <ArrowRight aria-hidden="true" /></button>
              <button class="download-button" type="button" :disabled="downloadingId === item.id" :aria-label="`${downloadLabel} de ${item.id}`" :title="downloadingId === item.id ? 'Generando PDF...' : downloadLabel" @click="emit('download', item)"><Download aria-hidden="true" /></button>
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-else>
        <tr>
          <td colspan="7" class="empty-cell">
            <strong>{{ emptyTitle }}</strong>
            <span>{{ emptyDescription }}</span>
            <RouterLink v-if="emptyTo" class="button" :to="emptyTo">Iniciar una interpretación <ArrowRight aria-hidden="true" /></RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.history-table-scroll { overflow-x: auto; }
.history-table { width: 100%; min-width: 1000px; border-collapse: collapse; text-align: left; }
.history-table th { padding: 14px 16px; background: #eaf5fd; color: var(--navy); font-size: 13px; font-weight: 600; white-space: nowrap; }
.history-table td { height: 78px; padding: 11px 16px; border-bottom: 1px solid #e4edf3; color: var(--ink); font-size: 13px; vertical-align: middle; }
.history-table tbody tr:last-child td { border-bottom: 0; }
.history-table td strong, .history-table td small { display: block; }
.history-table td strong { color: var(--navy); font-size: 14px; }
.history-table td small { margin-top: 5px; color: var(--muted); font-size: 12px; }
.date-cell, .id-cell, .model-cell { white-space: nowrap; }
.image-count-cell { display: flex; align-items: center; gap: 11px; }
.image-stack { position: relative; display: block; flex: 0 0 60px; width: 60px; height: 49px; }
.stack-card, .image-stack > img, .stack-placeholder { position: absolute; top: 0; width: 39px; height: 49px; border: 1px solid #d5e1ea; border-radius: 9px; background: #edf3f7; }
.stack-back { left: 18px; background: #e4edf4; }
.stack-middle { left: 9px; background: #f1f6fa; }
.image-stack > img { left: 0; object-fit: cover; }
.stack-placeholder { display: grid; left: 0; place-items: center; color: var(--brand); }
.stack-placeholder svg { width: 22px; height: 22px; }
.count-pill { padding: 7px 10px; border-radius: 8px; background: #eff5fa; color: #47647d; font-size: 12px; white-space: nowrap; }
.roi-count { white-space: nowrap; }
.completed-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 20px; background: #e4f8ef; color: #167451; font-size: 12px; font-weight: 600; white-space: nowrap; }
.completed-badge > span { display: inline-grid; width: 17px; height: 17px; place-items: center; border-radius: 50%; background: #20b77b; color: #fff; font-size: 12px; font-weight: 700; }
.experimental-note { margin-left: 4px; }
.row-actions { display: flex; align-items: center; gap: 9px; }
.open-button, .download-button { display: inline-flex; align-items: center; justify-content: center; min-height: 38px; border: 1px solid var(--brand); border-radius: 9px; background: #fff; color: #0965a1; font-size: 13px; font-weight: 600; cursor: pointer; }
.open-button { gap: 7px; padding: 0 13px; white-space: nowrap; }
.open-button:hover, .download-button:hover { background: #eef8ff; }
.open-button svg { width: 16px; height: 16px; }
.download-button { width: 40px; padding: 0; }
.download-button:disabled { opacity: .55; cursor: wait; }
.download-button svg { width: 18px; height: 18px; }
.empty-cell { padding: 36px 18px !important; text-align: center; }
.empty-cell strong { margin-bottom: 5px; font-size: 16px !important; }
.empty-cell > span { color: var(--muted); }
.empty-cell .button { display: flex; width: fit-content; margin: 16px auto 0; font-size: 13px; }
</style>
