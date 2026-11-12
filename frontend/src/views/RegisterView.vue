<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'

const router = useRouter()
// Datos escritos por la persona durante la creación de su perfil.
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const legalAccepted = ref(false)
const error = ref('')

// Comprueba que los campos estén completos y que las contraseñas coincidan.
// Cuando pasa la validación, el prototipo continúa al dashboard sin guardar en servidor.
function submit() {
  error.value = ''

  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Completa todos los campos para continuar.'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  if (!legalAccepted.value) {
    error.value = 'Debes aceptar el aviso legal para crear tu cuenta.'
    return
  }

  router.push('/inicio')
}
</script>

<template>
  <!-- AuthLayout comparte con acceso el fondo y la tarjeta informativa lateral. -->
  <AuthLayout
    headline="Empieza tu cuaderno de interpretaciones."
    introduction="Organiza imágenes, revisa regiones de interés y consulta tus análisis experimentales."
  >
    <!-- Formulario de registro. @submit.prevent evita recargar y llama a submit(). -->
    <form class="auth-form" @submit.prevent="submit">
      <!-- Encabezado propio de la pantalla de registro. -->
      <div class="form-heading">
        <h1>Crear cuenta</h1>
      </div>

      <!-- Enlace alterno al inicio de sesión para cuentas existentes. -->
      <p class="auth-switch">¿Ya tienes cuenta? <RouterLink to="/acceso">Inicia sesión</RouterLink></p>

      <!-- Nombre que se asociará a la cuenta nueva. -->
      <label class="auth-field">
        Nombre completo
        <input
          v-model="name"
          type="text"
          autocomplete="name"
          placeholder="Ej. María Pérez"
          required
        />
      </label>

      <!-- Correo que se usaría para identificar la cuenta. -->
      <label class="auth-field">
        Correo electrónico
        <input
          v-model="email"
          type="email"
          autocomplete="email"
          placeholder="nombre@correo.com"
          required
        />
      </label>

      <!-- Contraseña nueva; el navegador solicita al menos ocho caracteres. -->
      <label class="auth-field">
        Contraseña
        <input
          v-model="password"
          type="password"
          autocomplete="new-password"
          placeholder="Mínimo 8 caracteres"
          minlength="8"
          required
        />
      </label>

      <!-- Campo separado que permite comprobar que ambas contraseñas coincidan. -->
      <label class="auth-field">
        Confirmar contraseña
        <input
          v-model="confirmPassword"
          type="password"
          autocomplete="new-password"
          placeholder="Vuelve a escribir tu contraseña"
          minlength="8"
          required
        />
      </label>

      <!-- Mensaje de error si falta algún dato o las contraseñas son distintas. -->
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <!-- Aceptación requerida; el texto forma parte del área clicable del checkbox. -->
      <label class="legal-consent">
        <input v-model="legalAccepted" type="checkbox" name="legalAccepted" required />
        <span>
          Entiendo que ColorrectalAI es una herramienta académica experimental, que sus resultados
          no constituyen un diagnóstico médico y que deben ser interpretados por un profesional de salud.
        </span>
      </label>

      <!-- Acción principal para crear la cuenta. -->
      <button class="button" type="submit">Crear mi cuenta <span>→</span></button>
    </form>
  </AuthLayout>
</template>

<style scoped>
/* El consentimiento se alinea en dos columnas para que el texto no desplace la casilla. */
.legal-consent {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  align-items: start;
  gap: 10px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 400;
  line-height: 1.55;
  cursor: pointer;
}

/* Tamaño y color propios para que el checkbox no herede el formato de los campos de texto. */
.legal-consent input[type='checkbox'] {
  width: 17px;
  height: 17px;
  margin: 2px 0 0;
  padding: 0;
  accent-color: var(--brand);
  cursor: pointer;
}
</style>
