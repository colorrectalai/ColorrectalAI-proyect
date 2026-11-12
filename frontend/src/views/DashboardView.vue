<script setup>
import PageHead from '../components/PageHead.vue'
import HistoryTable from '../components/HistoryTable.vue'

// Datos de demostración que se envían a la tabla de actividad reciente.
const recent=[
 {date:'18 oct 2025',time:'10:42 a. m.',id:'A-DEMO-003',case:'Colonoscopia · Caso de práctica',count:3,confidence:'94.2%',label:'Alta',status:'Completado',note:'18 oct 2025, 10:43'},
 {date:'17 oct 2025',time:'3:16 p. m.',id:'A-DEMO-002',case:'Colonoscopia · Caso de práctica',count:2,confidence:'91.8%',label:'Alta',status:'Completado',note:'17 oct 2025, 3:17'}]
</script>
<template>
  <main class="page dashboard">
    <!-- Título, descripción y acceso rápido para iniciar otra interpretación. -->
    <PageHead
      eyebrow="CUADERNO ACADÉMICO / RESUMEN"
      title="Inicio"
      description="Hola, Juan. Este es el resumen de tu actividad reciente."
      action="Nueva interpretación"
    />

    <!-- Tarjetas con el resumen numérico de la actividad académica. -->
    <section class="stats">
      <!-- Total de análisis que aparecen en el cuaderno. -->
      <article>
        <span>▧</span><div><small>Interpretaciones guardadas</small><b>24</b></div>
        <i>En tu cuaderno académico</i>
      </article>
      <!-- Cantidad acumulada de imágenes analizadas. -->
      <article>
        <span>◎</span><div><small>Imágenes analizadas</small><b>37</b></div>
        <i>Entre todos los análisis</i>
      </article>
      <!-- Regiones sugeridas que se dejaron marcadas para revisar. -->
      <article>
        <span>◷</span><div><small>Posibles regiones de interés</small><b>8</b></div>
        <i>Marcadas para revisión</i>
      </article>
    </section>

    <!-- Encabezado de actividad y enlace al historial completo. -->
    <div class="dashboard-section-head">
      <div><p class="eyebrow">ACTIVIDAD RECIENTE</p><h2>Últimas interpretaciones</h2></div>
      <RouterLink to="/historial" class="row-link">Ver historial completo →</RouterLink>
    </div>

    <section class="panel">
      <!-- Tabla reutilizada que muestra los análisis recientes. -->
      <HistoryTable :items="recent" />

      <!-- Invitación a crear otro análisis desde el dashboard. -->
      <div class="dashboard-empty">
        <div class="empty-symbol">＋</div>
        <div><b>¿Listo para analizar nuevas imágenes?</b><p>Inicia una interpretación para visualizar las regiones de interés detectadas por el modelo experimental.</p></div>
        <RouterLink class="button" to="/carga">Nueva interpretación →</RouterLink>
      </div>
    </section>

    <!-- Aviso permanente sobre el uso académico de la herramienta. -->
    <p class="disclaimer">ⓘ　Recuerda: ColorrectalAI es una herramienta académica experimental y no reemplaza el diagnóstico médico.</p>
  </main>
</template>
<style scoped>
/* Distribución del encabezado de actividad y del bloque de invitación. */
.dashboard-section-head {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:15px;
  margin:30px 0 13px;
}
.dashboard-section-head h2 {
  margin:0;
  color:var(--navy);
  font-size:18px;
}
.dashboard-section-head .eyebrow {
  margin-bottom:6px;
}
.dashboard-empty {
  display:flex;
  align-items:center;
  gap:13px;
  padding:17px;
  border-top:1px solid var(--line);
}
.dashboard-empty > div:nth-child(2) {
  flex:1;
}
.dashboard-empty b {
  color:var(--navy);
  font-size:11px;
}
.dashboard-empty p {
  margin:5px 0 0;
  color:var(--muted);
  font-size:10px;
  line-height:1.5;
}
.empty-symbol {
  display:grid;
  width:36px;
  height:36px;
  flex:0 0 auto;
  place-items:center;
  border-radius:7px;
  background:var(--brand-soft);
  color:var(--brand);
  font-size:21px;
}
@media (max-width:620px) {
  .dashboard-section-head {
    align-items:flex-start;
    flex-direction:column;
  }
  .dashboard-empty {
    align-items:flex-start;
    flex-direction:column;
  }
}
</style>
