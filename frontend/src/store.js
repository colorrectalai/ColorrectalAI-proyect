// Estado compartido entre pantallas (carga → análisis → resultados). Solo vive en memoria.
import { reactive } from 'vue'

export const estado = reactive({
  archivos: [],     // imágenes elegidas en /carga
  resultados: [],   // { nombre, url, respuesta } por cada imagen analizada
  id: '',           // identificador de la interpretación
})
