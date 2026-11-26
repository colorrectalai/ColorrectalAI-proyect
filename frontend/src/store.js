// Estado compartido entre pantallas (carga → análisis → resultados). Solo vive en memoria.
import { reactive } from 'vue'

export const estado = reactive({
  archivos: [],     // imágenes elegidas en /carga
  resultados: [],   // { nombre, url, respuesta } por cada imagen analizada
  fallidos: [],     // { nombre, mensaje } por cada imagen que la API rechazó en el último análisis
  id: '',           // identificador de la interpretación actual
  historialError: '', // aviso si no se pudo guardar una interpretación localmente
})

// Libera las URL temporales al reemplazar resultados por una nueva interpretación.
export function liberarUrlsResultados() {
  estado.resultados.forEach((resultado) => {
    if (resultado.url?.startsWith('blob:')) URL.revokeObjectURL(resultado.url)
  })
}