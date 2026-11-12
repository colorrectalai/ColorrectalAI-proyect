<script setup>
import PageHead from '../components/PageHead.vue'

// Casos de ejemplo para mostrar cómo se llena el historial.
const items=[
 {date:'18 oct 2025',time:'10:42 a. m.',id:'A-DEMO-003',case:'Colonoscopia · Caso de práctica',count:3,confidence:'94.2%',label:'Alta',status:'Completado',note:'18 oct 2025, 10:43'},
 {date:'17 oct 2025',time:'3:16 p. m.',id:'A-DEMO-002',case:'Colonoscopia · Caso de práctica',count:2,confidence:'91.8%',label:'Alta',status:'Completado',note:'17 oct 2025, 3:17'},
 {date:'16 oct 2025',time:'9:08 a. m.',id:'A-DEMO-001',case:'Colonoscopia · Caso de práctica',count:4,confidence:'87.6%',label:'Media',status:'Completado',note:'16 oct 2025, 9:09'},
]
</script>
<template>
  <main class="page">
    <!-- Título de página y acción para iniciar una interpretación. -->
    <PageHead
      eyebrow="CUADERNO ACADÉMICO / HISTORIAL"
      title="Historial de interpretaciones"
      description="Revisa, filtra y consulta el detalle de tus análisis experimentales."
      action="Nueva interpretación"
    />

    <!-- Indicadores generales de los análisis almacenados. -->
    <section class="stats">
      <!-- Total de interpretaciones disponibles en el historial. -->
      <article>
        <span>▧</span><div><small>Interpretaciones guardadas</small><b>24</b></div>
        <i>En tu cuaderno académico</i>
      </article>
      <!-- Número de imágenes contenidas en los análisis. -->
      <article>
        <span>◎</span><div><small>Imágenes analizadas</small><b>37</b></div>
        <i>Entre todos los análisis</i>
      </article>
      <!-- Regiones detectadas de forma experimental para revisión visual. -->
      <article>
        <span>◷</span><div><small>Posibles regiones de interés</small><b>8</b></div>
        <i>Sugeridas para revisión visual</i>
      </article>
    </section>

    <section class="panel">
      <!-- Controles de maqueta para búsqueda y fecha; aún no filtran los datos. -->
      <div class="filters">
        <input placeholder="⌕  Buscar por identificador, fecha o caso" />
        <button>▦　Seleccionar fechas</button>
        <span>Los resultados corresponden a interpretaciones experimentales.</span>
      </div>

      <!-- Tabla compartida con el dashboard para listar interpretaciones. -->
      <HistoryTable :items="items" />

      <!-- Controles de paginación de muestra. -->
      <footer class="pagination">
        Mostrando 3 de 24 interpretaciones
        <div><button>‹</button><button class="selected">1</button><button>2</button><button>3</button><button>…</button><button>8</button><button>›</button></div>
      </footer>
    </section>

    <!-- Aviso acerca del uso y alcance académico de los resultados. -->
    <p class="disclaimer">ⓘ　ColorrectalAI es una herramienta académica experimental. Los resultados pueden contener errores y no constituyen un diagnóstico médico.</p>
  </main>
</template>
<style scoped>
/* Estilos de búsqueda, paginación y adaptación del historial en móvil. */
.filters {
  min-height:70px;
  display:flex;
  align-items:center;
  gap:10px;
  padding:13px 16px;
  border-bottom:1px solid var(--line);
}
.filters input {
  width:min(340px,42%);
  height:36px;
  padding:0 11px;
  border:1px solid #d5e1e8;
  border-radius:5px;
  background:#fff;
  color:var(--ink);
  font-size:10px;
}
.filters input::placeholder {
  color:#8a9daa;
}
.filters button {
  height:36px;
  padding:0 11px;
  border:1px solid #d5e1e8;
  border-radius:5px;
  background:#fff;
  color:var(--ink);
  font-size:10px;
  cursor:pointer;
}
.filters > span {
  margin-left:auto;
  color:var(--quiet);
  font-size:9px;
  text-align:right;
}
.filters + :deep(.table-scroll) {
  overflow-x:auto;
}
.filters ~ :deep(.table-scroll .records) {
  min-width:900px;
}
.pagination {
  min-height:52px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  padding:0 16px;
  color:var(--muted);
  font-size:9px;
}
.pagination > div {
  display:flex;
  gap:4px;
}
.pagination button {
  min-width:27px;
  height:27px;
  border:1px solid #d5e1e8;
  border-radius:4px;
  background:#fff;
  color:var(--ink);
  font-size:10px;
  cursor:pointer;
}
.pagination button.selected {
  border-color:var(--brand);
  background:var(--brand);
  color:#fff;
}
@media (max-width:900px) {
  .filters {
    flex-wrap:wrap;
  }
  .filters input {
    width:100%;
  }
  .filters > span {
    width:100%;
    margin:0;
    text-align:left;
  }
}
@media (max-width:620px) {
  .filters {
    padding:12px;
  }
  .filters button {
    width:100%;
  }
  .pagination {
    align-items:flex-start;
    flex-direction:column;
    padding:12px;
  }
}
</style>
