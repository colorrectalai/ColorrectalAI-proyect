<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BrandLogo from '../components/BrandLogo.vue'
import { analizarImagen } from '../api'
import { guardarInterpretacion } from '../history'
import { estado, liberarUrlsResultados } from '../store'

const router = useRouter()
const hechas = ref(0)
const error = ref('')
const total = computed(() => estado.archivos.length)
const porcentaje = computed(() => (total.value ? Math.round((hechas.value / total.value) * 100) : 0))

// Envía cada imagen a la API, una tras otra. Si una falla, se anota su error y se sigue con
// las demás (CF-02): un archivo rechazado no impide analizar el resto del lote.
onMounted(async () => {
  if (!total.value) return router.replace('/carga')
  liberarUrlsResultados()
  estado.resultados = []
  estado.fallidos = []
  estado.historialError = ''
  const analizadas = []
  for (const archivo of estado.archivos) {
    try {
      const respuesta = await analizarImagen(archivo)
      estado.resultados.push({ nombre: archivo.name, url: URL.createObjectURL(archivo), respuesta })
      analizadas.push(archivo)
    } catch (e) {
      estado.fallidos.push({ nombre: archivo.name, mensaje: e.message })
    } finally {
      hechas.value++
    }
  }

  if (!estado.resultados.length) {
    error.value = estado.fallidos.length === 1
      ? estado.fallidos[0].mensaje
      : 'No se pudo analizar ninguna de las imágenes. ' +
        estado.fallidos.map((fallo) => `${fallo.nombre}: ${fallo.mensaje}`).join(' ')
    return
  }

  // Los resultados quedan alineados con sus archivos para el historial y para reabrirlos.
  estado.archivos = analizadas
  estado.id = 'A-' + estado.resultados[0].respuesta.id.slice(0, 6).toUpperCase()
  try {
    await guardarInterpretacion({
      id: estado.id,
      createdAt: new Date().toISOString(),
      resultados: estado.resultados.map((resultado, index) => ({
        nombre: resultado.nombre,
        archivo: analizadas[index],
        respuesta: resultado.respuesta,
      })),
    })
  } catch (errorGuardar) {
    console.error('No se pudo guardar la interpretación en el historial local:', errorGuardar)
    estado.historialError = errorGuardar.message || 'No se pudo guardar la interpretación en este navegador.'
  }
  // La interpretación ya terminó; deja vacía la selección para la próxima carga.
  estado.archivos = []
  router.replace('/resultados/' + estado.id)
})
</script>

<template>
  <!-- Capa oscura que enfoca la atención en el cuadro de progreso. -->
  <div class="modal-screen">
    <div class="progress-dialog">
      <BrandLogo />
      <h2>{{ error ? 'No se pudo completar el análisis' : 'Analizando imágenes' }}</h2>
      <p v-if="error" class="fallo">{{ error }}</p>
      <p v-else>ColorrectalAI es una herramienta académica experimental. Sus resultados pueden contener errores y no constituyen un diagnóstico médico.</p>
      <template v-if="!error">
        <div class="progress-track"><i :style="{ width: Math.max(porcentaje, 8) + '%' }"></i></div>
        <small>En curso · {{ hechas }} de {{ total }} imágenes</small>
      </template>
      <RouterLink v-else class="button volver" to="/carga">Volver a cargar</RouterLink>
    </div>
  </div>
</template>
<style scoped>
/* Fondo que cubre la vista mientras se muestra el estado de análisis. */
.modal-screen {
  position:fixed;
  inset:0;
  z-index:30;
  display:grid;
  place-items:center;
  padding:18px;
  background:#0b294a7a;
  backdrop-filter:blur(3px);
}
/* Tarjeta central que contiene el estado y la explicación experimental. */
.progress-dialog {
  width:min(380px,100%);
  padding:28px 30px 24px;
  border:1px solid #d9e5ec;
  border-radius:10px;
  background:#fff;
  box-shadow:0 24px 70px #071e3650;
  text-align:center;
}
.progress-dialog > :deep(.brand-lockup) {
  justify-content:center;
}
.progress-dialog :deep(.brand-name) {
  color:var(--navy);
}
.progress-dialog :deep(.brand-lockup small) {
  color:var(--muted);
}
.progress-dialog h2 {
  margin:19px 0 9px;
  color:var(--navy);
  font-size:17px;
}
.progress-dialog p {
  margin:0;
  color:var(--muted);
  font-size:10px;
  line-height:1.6;
  text-align:left;
}
.progress-track {
  height:7px;
  overflow:hidden;
  margin-top:21px;
  border-radius:7px;
  background:#e8f0f4;
}
.progress-track i {
  display:block;
  height:100%;
  border-radius:inherit;
  background:var(--brand-bright);
  transition:width .35s ease;
}
.progress-dialog > small {
  display:block;
  margin-top:8px;
  color:var(--brand);
  font-size:9px;
  text-align:right;
}
/* La barra avanza durante la misma ventana que dura la simulación. */
@keyframes progress {
  to {
    width:100%;
  }
}
.fallo {
  color:#b3261e !important;
  font-size:11px !important;
  text-align:center !important;
}
.volver {
  display:inline-block;
  margin-top:18px;
}
@media (max-width: 480px) {
  .progress-dialog { padding: 24px 20px 20px; }
  .progress-dialog p { font-size: 12px; }
  .progress-dialog > small { font-size: 11px; }
  .volver { width: 100%; }
}
</style>
