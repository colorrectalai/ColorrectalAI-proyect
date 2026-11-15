<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, CalendarDays, FileImage, Images, Info, ScanSearch, Search } from '@lucide/vue'
import PageHead from '../components/PageHead.vue'
import InterpretationHistoryTable from '../components/InterpretationHistoryTable.vue'
import { descargarResumen, listarInterpretaciones, restaurarInterpretacion } from '../history'
import { estado } from '../store'

const router = useRouter()
const interpretaciones = ref([])
const terminoBusqueda = ref('')
const periodo = ref('todas')
const masRecientesPrimero = ref(true)
const paginaActual = ref(1)
const cargando = ref(true)
const errorHistorial = ref('')
const errorAccion = ref('')
const tamanoPagina = 5

// Totales calculados con los registros reales que se guardaron en este navegador.
const totalImagenes = computed(() =>
  interpretaciones.value.reduce((total, item) => total + item.resultados.length, 0),
)
const totalRegiones = computed(() =>
  interpretaciones.value.reduce(
    (total, item) => total + item.resultados.reduce((suma, resultado) => suma + (resultado.respuesta.rois?.length || 0), 0),
    0,
  ),
)

// Convierte cada registro técnico a los datos que necesita la tabla.
const filas = computed(() => interpretaciones.value.map((item) => {
  const fecha = new Date(item.createdAt)
  const rois = item.resultados.reduce((total, resultado) => total + (resultado.respuesta.rois?.length || 0), 0)
  const modelo = item.resultados.find((resultado) => resultado.respuesta.modelo_version)?.respuesta.modelo_version || 'Modelo experimental'
  return {
    ...item,
    fecha,
    cantidadImagenes: item.resultados.length,
    regiones: rois,
    modelo,
  }
}))

const filtradas = computed(() => {
  const consulta = terminoBusqueda.value.trim().toLocaleLowerCase('es-CO')
  const ahora = new Date()
  const hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate())

  const coincidencias = filas.value.filter((item) => {
    const coincideBusqueda = !consulta || item.id.toLocaleLowerCase('es-CO').includes(consulta)
    if (!coincideBusqueda) return false
    if (periodo.value === 'todas') return true
    if (Number.isNaN(item.fecha.getTime())) return false
    if (periodo.value === 'hoy') return item.fecha >= hoy
    const dias = Number(periodo.value)
    const limite = new Date(ahora)
    limite.setDate(limite.getDate() - dias)
    return item.fecha >= limite
  })

  return coincidencias.sort((a, b) => masRecientesPrimero.value
    ? b.fecha - a.fecha
    : a.fecha - b.fecha)
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(filtradas.value.length / tamanoPagina)))
const paginas = computed(() => Array.from({ length: totalPaginas.value }, (_, index) => index + 1))
const elementosPagina = computed(() => {
  const inicio = (paginaActual.value - 1) * tamanoPagina
  return filtradas.value.slice(inicio, inicio + tamanoPagina)
})
const textoPaginacion = computed(() => {
  if (!filtradas.value.length) return 'Mostrando 0 de 0 interpretaciones'
  const inicio = (paginaActual.value - 1) * tamanoPagina + 1
  const fin = Math.min(paginaActual.value * tamanoPagina, filtradas.value.length)
  return `Mostrando ${inicio}–${fin} de ${filtradas.value.length} interpretaciones`
})

// Carga los registros locales; la tabla solicita miniaturas solo de las filas visibles.
onMounted(async () => {
  try {
    interpretaciones.value = await listarInterpretaciones()
  } catch (error) {
    errorHistorial.value = error.message || 'No se pudo cargar el historial local.'
  } finally {
    cargando.value = false
  }
})

watch([terminoBusqueda, periodo], () => {
  paginaActual.value = 1
})
watch(totalPaginas, (total) => {
  if (paginaActual.value > total) paginaActual.value = total
})

// Restaura los archivos desde IndexedDB y abre esa interpretación en el visor habitual.
const abrirInterpretacion = async (item) => {
  errorAccion.value = ''
  try {
    await restaurarInterpretacion(item.id)
    await router.push({ name: 'results', params: { id: item.id } })
  } catch (error) {
    errorAccion.value = error.message || 'No se pudo abrir esta interpretación.'
  }
}

</script>

<template>
  <main class="page history-page">
    <!-- Encabezado de historial y acceso directo para iniciar otra interpretación. -->
    <PageHead
      eyebrow="CUADERNO ACADÉMICO / HISTORIAL"
      title="Historial de interpretaciones"
      description="Recupera cada análisis con sus imágenes y resultados experimentales."
      action="Nuevo análisis"
      to="/carga"
    />

    <!-- Resumen de los análisis e imágenes registrados en este navegador. -->
    <section class="history-stats" aria-label="Resumen del historial">
      <article class="history-stat">
        <span class="stat-icon"><ScanSearch aria-hidden="true" /></span>
        <strong class="stat-number">{{ interpretaciones.length }}</strong>
        <div><b>Análisis completados</b><small>Guardados en este navegador</small></div>
      </article>
      <article class="history-stat">
        <span class="stat-icon"><FileImage aria-hidden="true" /></span>
        <strong class="stat-number">{{ totalImagenes }}</strong>
        <div><b>Imágenes procesadas</b><small>En tus interpretaciones</small></div>
      </article>
      <article class="history-stat">
        <span class="stat-icon"><Images aria-hidden="true" /></span>
        <strong class="stat-number">{{ totalRegiones }}</strong>
        <div><b>Regiones de interés</b><small>Señaladas por el modelo</small></div>
      </article>
    </section>

    <!-- Búsqueda, filtro por antigüedad y orden de los registros. -->
    <section class="history-panel" aria-label="Interpretaciones guardadas">
      <div class="history-toolbar">
        <label class="search-control">
          <Search aria-hidden="true" />
          <input v-model="terminoBusqueda" type="search" placeholder="Buscar por ID de análisis..." />
        </label>
        <label class="date-control">
          <CalendarDays aria-hidden="true" />
          <select v-model="periodo" aria-label="Filtrar por fecha">
            <option value="todas">Todas las fechas</option>
            <option value="hoy">Hoy</option>
            <option value="7">Últimos 7 días</option>
            <option value="30">Últimos 30 días</option>
          </select>
        </label>
        <button class="sort-control" type="button" @click="masRecientesPrimero = !masRecientesPrimero">
          {{ masRecientesPrimero ? 'Más recientes primero' : 'Más antiguos primero' }}
          <ArrowDown :class="{ reversed: !masRecientesPrimero }" aria-hidden="true" />
        </button>
      </div>

      <p v-if="errorAccion" class="history-error" role="alert">{{ errorAccion }}</p>
      <p v-if="errorHistorial" class="history-error" role="alert">{{ errorHistorial }}</p>
      <p v-if="estado.historialError" class="history-error" role="status">
        El análisis terminó, pero no se guardó en el historial local: {{ estado.historialError }}
      </p>

      <!-- Tabla compartida con Dashboard, con los datos reales del historial local. -->
      <InterpretationHistoryTable
        :items="elementosPagina"
        :loading="cargando"
        :empty-title="errorHistorial ? 'No se pudo cargar el historial' : interpretaciones.length ? 'No hay resultados para estos filtros' : 'Todavía no hay interpretaciones guardadas'"
        :empty-description="errorHistorial ? 'Revisa el almacenamiento local e inténtalo de nuevo.' : interpretaciones.length ? 'Prueba con otro ID o periodo.' : 'Cuando completes un análisis, aparecerá aquí.'"
        :empty-to="!errorHistorial && !interpretaciones.length ? '/carga' : ''"
        @open="abrirInterpretacion"
        @download="descargarResumen"
      />

      <!-- Navegación entre páginas de resultados filtrados. -->
      <footer class="history-pagination">
        <span>{{ textoPaginacion }}</span>
        <div class="page-controls" aria-label="Paginación del historial">
          <button type="button" :disabled="paginaActual <= 1" @click="paginaActual--">Anterior</button>
          <button
            v-for="pagina in paginas"
            :key="pagina"
            type="button"
            :class="{ selected: pagina === paginaActual }"
            :aria-current="pagina === paginaActual ? 'page' : undefined"
            @click="paginaActual = pagina"
          >{{ pagina }}</button>
          <button type="button" :disabled="paginaActual >= totalPaginas" @click="paginaActual++">Siguiente</button>
        </div>
      </footer>
    </section>

    <!-- Aviso sobre el uso académico y el almacenamiento local de registros. -->
    <p class="history-disclaimer"><Info aria-hidden="true" /><span>Resultados experimentales para investigación y educación. No constituyen un diagnóstico ni reemplazan la evaluación de un profesional de la salud. El historial se guarda en este navegador.</span></p>
  </main>
</template>

<style scoped>

/* Encabezado y tarjetas de resumen alineados con el sistema visual existente. */
.history-page {
  position: relative;
  isolation: isolate;
}

.history-page::before {
  content: "";
  position: absolute;
  inset: -20px calc((100% - 100vw) / 2); /* Extiende la capa hasta ambos bordes del viewport */
  z-index: -1;
  pointer-events: none;

  background: url("/img/Fondo4.png") center / cover no-repeat;

  filter: blur(4px); /* Desenfoca directamente la imagen de esta capa */
}

.history-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.history-stat {
  display: grid;
  grid-template-columns: 54px auto minmax(0, 1fr);
  align-items: center;
  gap: 13px;
  min-height: 94px;
  padding: 16px 18px;
  border: 1px solid #d6e7f3;
  border-radius: 16px;
  background: #fff;
  box-shadow: var(--shadow);
}

.stat-icon {
  display: grid;
  width: 50px;
  height: 50px;
  place-items: center;
  border-radius: 13px;
  background: #e6f5ff;
  color: var(--brand);
}

.stat-icon svg {
  width: 25px;
  height: 25px;
}

.stat-number {
  color: var(--navy);
  font-size: 32px;
  line-height: 1;
}

.history-stat b,
.history-stat small {
  display: block;
}

.history-stat b {
  color: var(--navy);
  font-size: 15px;
  white-space: nowrap;
}

.history-stat small {
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
}

/* Panel blanco y controles funcionales de historial. */
.history-panel {
  overflow: hidden;
  border: 1px solid #d6e7f3;
  border-radius: 16px;
  background: #fff;
  box-shadow: var(--shadow);
}

.history-toolbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 15px 18px;
  border-bottom: 1px solid #e3edf4;
}

.search-control,
.date-control {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0 13px;
  border: 1px solid #bdd7eb;
  border-radius: 10px;
  background: #fff;
  color: var(--brand);
}

.search-control {
  flex: 1 1 430px;
  max-width: 530px;
}

.search-control svg,
.date-control svg {
  flex: 0 0 auto;
  width: 20px;
  height: 20px;
}

.search-control input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  color: var(--ink);
  font-size: 14px;
}

.search-control input::placeholder {
  color: #738ba0;
}

.search-control:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgb(0 157 255 / 12%);
}

.date-control {
  flex: 0 0 auto;
  color: var(--brand);
}

.date-control select {
  max-width: 190px;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--navy);
  font-size: 14px;
  cursor: pointer;
}

.sort-control {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 42px;
  margin-left: auto;
  padding: 0 8px;
  border: 0;
  background: transparent;
  color: #526b80;
  font-size: 13px;
  white-space: nowrap;
  cursor: pointer;
}

.sort-control svg {
  width: 18px;
  height: 18px;
  color: var(--navy);
  transition: transform 150ms ease;
}

.sort-control svg.reversed {
  transform: rotate(180deg);
}

.history-error {
  margin: 12px 18px 0;
  padding: 10px 12px;
  border: 1px solid #f1d0c8;
  border-radius: 8px;
  background: #fff7f4;
  color: #8d3b2e;
  font-size: 13px;
  line-height: 1.5;
}

/* Paginación y aviso académico bajo el panel. */
.history-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 60px;
  padding: 10px 18px;
  border-top: 1px solid #e4edf3;
  color: var(--muted);
  font-size: 13px;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 7px;
}

.page-controls button {
  min-width: 34px;
  height: 34px;
  padding: 0 9px;
  border: 0;
  border-radius: 20px;
  background: transparent;
  color: #546e83;
  font-size: 13px;
  cursor: pointer;
}

.page-controls button.selected {
  background: #dff3ff;
  color: #006bb0;
  font-weight: 700;
}

.page-controls button:disabled {
  opacity: 0.42;
  cursor: not-allowed;
}

.history-disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin: 18px 0 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}

.history-disclaimer svg {
  flex: 0 0 auto;
  width: 17px;
  height: 17px;
  color: var(--brand);
}

@media (max-width: 1050px) {
  .history-stats {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .history-stat {
    min-height: 78px;
  }

  .history-toolbar {
    flex-wrap: wrap;
  }

  .search-control {
    flex-basis: 100%;
    max-width: none;
  }

  .sort-control {
    margin-left: auto;
  }
}

@media (max-width: 620px) {
  .history-page :deep(.page-head .button) {
    width: 100%;
  }

  .history-stat {
    grid-template-columns: 48px auto minmax(0, 1fr);
    gap: 10px;
    padding: 12px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;
  }

  .stat-number {
    font-size: 28px;
  }

  .history-toolbar {
    align-items: stretch;
    padding: 12px;
  }

  .date-control,
  .sort-control {
    width: 100%;
    justify-content: flex-start;
  }

  .date-control select {
    flex: 1;
    max-width: none;
  }

  .history-pagination {
    align-items: flex-start;
    flex-direction: column;
    padding: 12px;
  }

  .page-controls {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
