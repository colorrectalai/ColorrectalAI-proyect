<script setup>
// La vista que usa la tabla entrega las interpretaciones como una lista de objetos.
defineProps({ items: { type: Array, default: () => [] } })
</script>
<template>
  <!-- Tabla reutilizable para el historial completo y la actividad reciente. -->
  <div class="table-scroll">
    <table class="records">
      <thead>
        <!-- Nombres de las columnas de cada interpretación guardada. -->
        <tr>
          <th>Fecha</th>
          <th>Identificador</th>
          <th>Imágenes</th>
          <th>Confianza</th>
          <th>Configuración</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <!-- Cada fila representa un análisis y enlaza a su ficha de detalle. -->
        <tr v-for="item in items" :key="item.id">
          <td><b>{{ item.date }}</b><small>{{ item.time }}</small></td>
          <td><b>{{ item.id }}</b><small>{{ item.case }}</small></td>
          <td>
            <span class="scope-thumb"><i></i></span>
            <span>{{ item.count }} imágenes</span>
          </td>
          <td><b>{{ item.confidence }}</b><small>{{ item.label }}</small></td>
          <td><b>Modelo experimental</b><small>Versión académica 1.0</small></td>
          <td><span class="status">{{ item.status }}</span><small>{{ item.note }}</small></td>
          <td>
            <!-- Este enlace funciona; la descarga es solo texto de muestra por ahora. -->
            <RouterLink :to="`/historial/${item.id}`" class="row-link">Ver detalle →</RouterLink>
            <small>Descargar informe</small>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<style scoped>
/* Permite desplazar la tabla horizontalmente cuando no cabe en pantallas estrechas. */
.table-scroll {
  overflow-x:auto;
}
.records {
  width:100%;
  border-collapse:collapse;
  text-align:left;
  white-space:nowrap;
}
.records th {
  background:#f1f6f9;
  color:#526b80;
  font-size:9px;
  font-weight:700;
  letter-spacing:.3px;
  padding:12px 13px;
  border-bottom:1px solid var(--line);
}
.records td {
  padding:11px 13px;
  color:#26435c;
  border-bottom:1px solid #e9eff3;
  font-size:10px;
}
.records tr:last-child td {
  border-bottom:0;
}
.records td b,.records td small {
  display:block;
}
.records td b {
  font-weight:600;
}
.records td small {
  font-size:9px;
  color:var(--quiet);
  margin-top:4px;
}
.records td:nth-child(3) {
  display:flex;
  align-items:center;
  gap:8px;
}
/* Miniatura decorativa que representa una imagen endoscópica con una región marcada. */
.scope-thumb {
  display:inline-block;
  flex:0 0 auto;
  width:38px;
  height:36px;
  border-radius:5px;
  background:radial-gradient(ellipse,#efa17d 4%,#a34844 34%,#23304a 76%);
  position:relative;
  overflow:hidden;
  vertical-align:middle;
}
.scope-thumb i {
  position:absolute;
  inset:32% auto auto 35%;
  width:31%;
  height:35%;
  border:2px solid #54c7cc;
  border-radius:45%;
}
</style>
