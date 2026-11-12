<script setup>
defineProps({
  headline: { type: String, required: true },
  introduction: { type: String, required: true },
})
</script>

<template>
  <main class="auth-page">
    <section class="auth-copy">
      <img class="auth-logo" src="../../public/img/Logotipo.png" alt="ColorrectalAI" />
      <h3 class="ColorrectalAI">Colorrectal<span>AI</span></h3>

      <div class="auth-message">
        <p class="auth-kicker">COLORRECTALAI · PLATAFORMA ACADÉMICA</p>
        <h2>{{ headline }}</h2>
        <p>{{ introduction }}</p>
      </div>

      <div class="auth-benefits">
        <div>
          <span>01</span>
          <p><b>Sube imágenes</b><small>JPG o PNG, una o varias por caso</small></p>
        </div>
        <div>
          <span>02</span>
          <p><b>Revisa el resultado</b><small>Consulta regiones sugeridas y confianza</small></p>
        </div>
        <div>
          <span>03</span>
          <p><b>Vuelve cuando quieras</b><small>Encuentra tus casos en el historial</small></p>
        </div>
      </div>

      <p class="auth-disclaimer">
        Herramienta de exploración académica. No sustituye la valoración de un especialista.
      </p>
    </section>

    <section class="auth-panel">
      <slot />
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: 60% 40%;
  align-items: stretch;
  width: 100%;
  min-height: 100svh;
}

.auth-copy {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  padding: clamp(36px, 5vw, 88px);
  background:
    linear-gradient(180deg, #071e3621 0%, #071e3633 42%, #071e36d9 100%),
    url('/img/FondoTecnologico.png') center / cover no-repeat;
}

.auth-logo {
  width: 80px;
  position: absolute;
  top: clamp(28px, 60px, 100px);
  left: clamp(36px, 70px, 88px);
  text-decoration: none;
}

.ColorrectalAI {
  position: absolute;
  top: clamp(28px, 55px, 150px);
  left: clamp(36px, 150px, 250px);
  color: #fff;
  font-size: 25px;
  font-weight: 700;
}

.ColorrectalAI span {
  color: #00abf5;
}

.auth-message {
  max-width: 580px;
  margin: auto 0 24px;
}

.auth-kicker {
  margin: 0 0 12px;
  color: #6bd6ee;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.437);
}

.auth-message h2 {
  margin: 0 0 12px;
  color: #fff;
  font-size: clamp(32px, 4vw, 50px);
  line-height: 1.16;
  letter-spacing: -1.2px;
}

.auth-message > p:last-child {
  max-width: 500px;
  margin: 0;
  color: #e0edf5;
  font-size: 15px;
  line-height: 1.7;
}

.auth-benefits {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.auth-benefits > div {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 9px;
  min-height: 104px;
  padding: 13px;
  border: 1px solid #ffffff1b;
  border-radius: 6px;
  background: #ffffff0a;
}

.auth-benefits > div > span {
  display: grid;
  width: 29px;
  height: 29px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: #00abf526;
  color: #76ddf0;
  font-size: 12px;
  font-weight: 700;
}

.auth-benefits p {
  display: grid;
  gap: 3px;
  margin: 0;
}

.auth-benefits b {
  color: #fff;
  font-size: 15px;
}

.auth-benefits small {
  color: #b4c9d7;
  font-size: 13px;
}

.auth-disclaimer {
  max-width: 540px;
  margin: 18px 0 0;
  color: #adc1cf;
  font-size: 12px;
  line-height: 1.6;
}

.auth-panel {
  display: grid;
  min-width: 0;
  place-items: center;
  padding: clamp(30px, 4vw, 72px);
  background: #fff;
}

.auth-panel :deep(.auth-form) {
  width: min(100%, 460px);
  min-height: min(80svh, 680px);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: clamp(12px, 1.8vh, 20px);
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.auth-panel :deep(.form-heading) {
  margin-bottom: 0;
  text-align: center;
}

.auth-panel :deep(.form-heading h1) {
  margin: 0;
  color: var(--navy-deep);
  font-size: clamp(27px, 2.5vw, 34px);
  letter-spacing: -0.8px;
}

.auth-panel :deep(.auth-form .auth-field) {
  display: block;
  color: #34536d;
  font-size: 11px;
  font-weight: 600;
}

.auth-panel :deep(.auth-form .auth-field input) {
  display: block;
  width: 100%;
  height: 50px;
  margin-top: 8px;
  padding: 0 14px;
  border: 1px solid #d2dfe7;
  border-radius: 8px;
  background: #fcfdfe;
  color: var(--ink);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.auth-panel :deep(.auth-form .auth-field input::placeholder) {
  color: #97a8b5;
}

.auth-panel :deep(.auth-form .auth-field input:focus) {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px #087fa81a;
}

.auth-panel :deep(.forgot-link) {
  align-self: center;
  margin-top: 0;
  color: var(--brand);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}

.auth-panel :deep(.forgot-link:hover),
.auth-panel :deep(.auth-switch a:hover) {
  text-decoration: underline;
}

.auth-panel :deep(.form-error) {
  margin: -4px 0 0;
  color: #b84045;
  font-size: 10px;
}

.auth-panel :deep(.auth-form > .button) {
  width: 100%;
  min-height: 50px;
  margin-top: 0;
  border-radius: 999px;
}

.auth-panel :deep(.auth-switch) {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  text-align: center;
}

.auth-panel :deep(.auth-switch a) {
  color: var(--brand);
  font-weight: 700;
  text-decoration: none;
}

.auth-panel :deep(.form-legal) {
  display: block;
  max-width: 100%;
  color: var(--quiet);
  font-size: 11px;
  line-height: 1.6;
  text-align: left;
}

@media (max-width: 900px) {
  .auth-copy {
    padding: 36px;
  }

  .auth-panel {
    padding: 30px;
  }
}

@media (max-width: 700px) {
  .auth-page {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .auth-copy {
    min-height: 390px;
    padding: 92px 24px 24px;
  }

  .auth-logo {
    top: 24px;
    left: 24px;
  }

  .auth-message {
    margin: 0 0 16px;
  }

  .auth-message h2 {
    font-size: 30px;
  }

  .auth-message > p:last-child {
    font-size: 13px;
  }

  .auth-benefits {
    gap: 7px;
  }

  .auth-benefits > div {
    min-height: 0;
    gap: 6px;
    padding: 9px;
  }

  .auth-benefits b {
    font-size: 9px;
  }

  .auth-benefits small {
    font-size: 8px;
  }

  .auth-disclaimer {
    margin-top: 12px;
  }

  .auth-panel {
    min-height: 540px;
    padding: 34px 24px 42px;
  }

  .auth-panel :deep(.auth-form) {
    min-height: 0;
    justify-content: flex-start;
    gap: 20px;
  }
}

@media (max-height: 760px) and (min-width: 701px) {
  .auth-panel :deep(.auth-form) {
    min-height: 0;
    justify-content: center;
    gap: 15px;
  }
}
</style>
