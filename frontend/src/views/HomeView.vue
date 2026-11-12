<template>
  <main class="page public-home">
    <!-- Presentación pública: explica el propósito y ofrece acceso o registro. -->
    <section class="home-hero">
      <!-- Texto principal y botones para entrar o crear una cuenta. -->
      <div class="home-copy">
        <p class="eyebrow">TECNOLOGÍA QUE ANALIZA · CIENCIA QUE PREVIENE</p>
        <h1>Explora imágenes de colonoscopia con una nueva perspectiva.</h1>
        <p>Una plataforma académica para revisar imágenes, visualizar regiones de interés y consultar resultados experimentales.</p>
        <div class="hero-actions">
          <RouterLink class="button" to="/registro">Crear cuenta <span>→</span></RouterLink>
          <RouterLink class="hero-secondary" to="/acceso">Ya tengo una cuenta</RouterLink>
        </div>
        <p class="hero-note"><span class="note-marker"></span>Prototipo académico · No brinda diagnósticos médicos</p>
      </div>

      <!-- Previsualización ilustrativa de una interpretación dentro del producto. -->
      <div class="home-visual">
        <div class="preview-toolbar"><BrandLogo compact /><span class="preview-user">DEMO</span></div>
        <div class="preview-content">
          <div class="preview-title">
            <div><small>VISTA PREVIA</small><b>Interpretación experimental</b></div>
            <span class="preview-state">Ejemplo</span>
          </div>
          <div class="preview-body">
            <div class="preview-colonoscopy">
              <div class="scope-large"><i></i><span>ROI 01</span></div>
              <div class="preview-image-footer">Imagen endoscópica <span>01 / 03</span></div>
            </div>
            <aside class="preview-analysis">
              <small>POSIBLE REGIÓN DE INTERÉS</small>
              <strong>Revisión sugerida</strong>
              <div class="preview-meter"><span></span></div>
              <b>94.2% <small>confianza experimental</small></b>
              <hr />
              <p>El resultado debe ser revisado por un profesional.</p>
            </aside>
          </div>
          <div class="preview-foot"><span>3 imágenes</span><span>Modelo académico</span><span>Sin diagnóstico</span></div>
        </div>
      </div>
    </section>

    <!-- Sección con los tres pasos principales del flujo de uso. -->
    <section class="how-section" id="acerca">
      <header>
        <p class="eyebrow">ASÍ FUNCIONA</p>
        <h2>De la imagen al análisis, paso a paso</h2>
        <p>Un espacio de práctica diseñado para acompañar la revisión visual.</p>
      </header>
      <div class="how-grid">
        <article><span>01</span><div><h3>Carga tus imágenes</h3><p>Añade imágenes endoscópicas de casos de práctica.</p></div><b>↗</b></article>
        <article><span>02</span><div><h3>Explora la interpretación</h3><p>Observa regiones sugeridas por el modelo experimental.</p></div><b>↗</b></article>
        <article><span>03</span><div><h3>Consulta tu historial</h3><p>Vuelve a tus análisis y revisa el detalle de cada caso.</p></div><b>↗</b></article>
      </div>
    </section>

    <!-- Marca y aclaración académica al pie de la página pública. -->
    <footer class="public-footer">
      <BrandLogo compact />
      <p>ColorrectalAI es una herramienta académica experimental. Sus resultados pueden contener errores y no sustituyen la evaluación de un médico especialista.</p>
    </footer>
  </main>
</template>
<script setup>
// Reutiliza el logo vectorial de la aplicación en la página pública.
import BrandLogo from '../components/BrandLogo.vue'
</script>
<style scoped>
/* Distribución del mensaje principal y su previsualización de producto. */
.public-home {
  padding-top: 24px;
}
.home-hero {
  display:grid;
  grid-template-columns:minmax(0,.88fr) minmax(0,1.12fr);
  align-items:center;
  gap:clamp(34px,5vw,72px);
  margin:12px 0 64px;
}
.home-copy {
  max-width:510px;
}
.home-copy h1 {
  max-width:540px;
  margin:0 0 17px;
  color:var(--navy-deep);
  font-size:clamp(36px,4vw,52px);
  line-height:1.08;
  letter-spacing:-1.8px;
}
.home-copy > p:not(.eyebrow):not(.hero-note) {
  max-width:460px;
  margin:0;
  color:var(--muted);
  font-size:15px;
  line-height:1.7;
}
.hero-actions {
  display:flex;
  align-items:center;
  gap:22px;
  margin-top:26px;
}
.hero-secondary {
  color:var(--brand);
  font-size:12px;
  font-weight:700;
  text-decoration:none;
}
.hero-secondary:hover {
  text-decoration:underline;
  text-underline-offset:3px;
}
.hero-note {
  display:flex;
  align-items:center;
  gap:8px;
  margin:23px 0 0;
  color:var(--quiet);
  font-size:10px;
}
.note-marker {
  width:7px;
  height:7px;
  border-radius:50%;
  background:var(--teal);
}
/* Tarjeta de muestra de una interpretación experimental. */
.home-visual {
  overflow:hidden;
  border:1px solid #d7e4ec;
  border-radius:10px;
  background:#fff;
  box-shadow:0 20px 55px #13395818;
}
.preview-toolbar {
  min-height:56px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 20px;
  background:var(--navy-deep);
}
.preview-user {
  padding:5px 8px;
  border:1px solid #41627d;
  border-radius:4px;
  color:#c1d4e1;
  font-size:8px;
  font-weight:700;
  letter-spacing:.7px;
}
.preview-content {
  padding:20px;
}
.preview-title {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin-bottom:15px;
}
.preview-title > div {
  display:grid;
  gap:5px;
}
.preview-title small,.preview-analysis > small {
  color:var(--quiet);
  font-size:8px;
  font-weight:700;
  letter-spacing:.65px;
}
.preview-title b {
  color:var(--navy);
  font-size:14px;
}
.preview-state {
  padding:5px 8px;
  border-radius:4px;
  background:var(--brand-soft);
  color:var(--brand);
  font-size:9px;
}
.preview-body {
  display:grid;
  grid-template-columns:minmax(0,1.5fr) minmax(145px,.8fr);
  gap:13px;
}
.preview-colonoscopy {
  min-width:0;
}
.preview-colonoscopy .scope-large {
  height:218px;
  margin:0;
  border-radius:6px;
}
.preview-image-footer {
  display:flex;
  justify-content:space-between;
  padding:9px 1px 0;
  color:var(--muted);
  font-size:9px;
}
.preview-analysis {
  align-self:stretch;
  padding:14px 12px;
  border:1px solid var(--line);
  border-radius:6px;
  background:#fbfdfe;
}
.preview-analysis strong {
  display:block;
  margin:10px 0 17px;
  color:var(--navy);
  font-size:13px;
}
.preview-meter {
  height:5px;
  overflow:hidden;
  border-radius:5px;
  background:#e4edf2;
}
.preview-meter span {
  display:block;
  width:94.2%;
  height:100%;
  border-radius:inherit;
  background:var(--teal);
}
.preview-analysis > b {
  display:block;
  margin-top:8px;
  color:var(--navy);
  font-size:15px;
}
.preview-analysis > b small {
  color:var(--quiet);
  font-size:8px;
  font-weight:400;
}
.preview-analysis hr {
  margin:14px 0 10px;
  border:0;
  border-top:1px solid var(--line);
}
.preview-analysis p {
  margin:0;
  color:var(--muted);
  font-size:9px;
  line-height:1.5;
}
.preview-foot {
  display:flex;
  justify-content:space-between;
  gap:10px;
  padding:11px 20px;
  border-top:1px solid #edf1f4;
  color:var(--quiet);
  font-size:8px;
}
/* Presentación de los pasos de uso y del aviso del pie de página. */
.how-section {
  padding:28px 0 48px;
  border-top:1px solid var(--line);
}
.how-section > header {
  max-width:550px;
  margin-bottom:22px;
}
.how-section h2 {
  margin:0 0 8px;
  color:var(--navy);
  font-size:25px;
  letter-spacing:-.5px;
}
.how-section header > p:last-child {
  margin:0;
  color:var(--muted);
  font-size:12px;
  line-height:1.6;
}
.how-grid {
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  border:1px solid var(--line);
  border-radius:8px;
  background:var(--surface);
}
.how-grid article {
  min-height:110px;
  display:grid;
  grid-template-columns:32px 1fr 16px;
  align-items:start;
  gap:12px;
  padding:20px 18px;
}
.how-grid article + article {
  border-left:1px solid var(--line);
}
.how-grid article > span {
  display:grid;
  width:30px;
  height:30px;
  place-items:center;
  border-radius:50%;
  background:var(--brand-soft);
  color:var(--brand);
  font-size:10px;
  font-weight:700;
}
.how-grid h3 {
  margin:2px 0 6px;
  color:var(--navy);
  font-size:12px;
}
.how-grid p {
  margin:0;
  color:var(--muted);
  font-size:10px;
  line-height:1.5;
}
.how-grid article > b {
  color:#8aa0b1;
  font-size:13px;
}
.public-footer {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:25px;
  padding:19px 0 0;
  border-top:1px solid var(--line);
}
.public-footer :deep(.brand-name) {
  color:var(--navy);
}
.public-footer :deep(.brand-lockup small) {
  color:var(--muted);
}
.public-footer p {
  max-width:610px;
  margin:0;
  color:var(--quiet);
  font-size:9px;
  line-height:1.6;
  text-align:right;
}
/* En tablet y móvil, la presentación pasa de columnas a una sola columna. */
@media (max-width:900px) {
  .home-hero {
    grid-template-columns:1fr;
    gap:30px;
    margin-bottom:42px;
  }
  .home-copy {
    max-width:680px;
  }
  .home-copy h1 {
    max-width:620px;
    font-size:clamp(35px,6vw,48px);
  }
}
@media (max-width:620px) {
  .public-home {
    padding-top:18px;
  }
  .home-hero {
    gap:24px;
    margin:0 0 36px;
  }
  .home-copy h1 {
    font-size:36px;
    letter-spacing:-1.2px;
  }
  .home-copy > p:not(.eyebrow):not(.hero-note) {
    font-size:13px;
  }
  .hero-actions {
    align-items:flex-start;
    gap:14px;
    flex-direction:column;
  }
  .preview-content {
    padding:14px;
  }
  .preview-body {
    grid-template-columns:1fr;
  }
  .preview-colonoscopy .scope-large {
    height:205px;
  }
  .preview-analysis {
    padding:12px;
  }
  .preview-foot {
    padding:10px 14px;
  }
  .how-section {
    padding:22px 0 32px;
  }
  .how-section h2 {
    font-size:21px;
  }
  .how-grid {
    grid-template-columns:1fr;
  }
  .how-grid article + article {
    border-top:1px solid var(--line);
    border-left:0;
  }
  .public-footer {
    align-items:flex-start;
    flex-direction:column;
    gap:12px;
  }
  .public-footer p {
    text-align:left;
  }
}
</style>
