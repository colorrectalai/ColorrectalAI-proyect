import { BookOpenText, CloudUpload, Images, ScanSearch } from '@lucide/vue'

// Etapas compartidas por la página pública y el espacio de trabajo.
export const workflowSteps = [
  { number: '01', icon: CloudUpload, title: 'Prepara las imágenes', description: 'Selecciona archivos JPG o PNG y verifica que no incluyan datos personales.' },
  { number: '02', icon: ScanSearch, title: 'Ejecuta el análisis', description: 'Consulta las etapas de procesamiento y conserva la configuración del ejemplo.' },
  { number: '03', icon: Images, title: 'Compara las salidas', description: 'Explora el original, la máscara de segmentación y la superposición de ROI.' },
  { number: '04', icon: BookOpenText, title: 'Documenta el contexto', description: 'Revisa la clasificación experimental, la predicción y el score de confianza.' },
]
