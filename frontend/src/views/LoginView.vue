<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'

const router = useRouter()
// Valores controlados por v-model en los campos del formulario.
const email = ref('')
const password = ref('')
// Mensaje de validación que se muestra debajo de los campos.
const error = ref('')

// Valida que haya datos y simula el acceso; todavía no consulta un servidor.
function submit() {
  error.value = ''

  if (!email.value || !password.value) {
    error.value = 'Completa tu correo y contraseña para continuar.'
    return
  }

  router.push('/inicio')
}
</script>

<template>
  <!-- AuthLayout dibuja la tarjeta informativa y recibe este formulario en su espacio. -->
  <AuthLayout
    headline="Tu cuaderno de análisis, en un solo lugar."
    introduction="Organiza imágenes, revisa regiones de interés y consulta tus análisis experimentales."
  >
    <!-- Formulario de acceso. @submit.prevent evita recargar y llama a submit(). -->
    <form class="auth-form" @submit.prevent="submit">
      <!-- Título del formulario y breve instrucción para el usuario. -->
      <div class="form-heading">
        <h1>Bienvenido de nuevo</h1>
      </div>

      <!-- Enlace alterno bajo el título, como acceso rápido al registro. -->
      <p class="auth-switch">¿Aún no tienes cuenta? <RouterLink to="/registro">Regístrate</RouterLink></p>

      <!-- Campo de correo, enlazado al estado reactivo email. -->
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

      <!-- Campo de contraseña para la cuenta existente. -->
      <label class="auth-field">
        Contraseña
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="Tu contraseña"
          minlength="8"
          required
        />
      </label>

      <!-- Mensaje de validación si faltan datos. -->
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <!-- Aviso de uso de datos de práctica. -->
      <small class="form-legal">
        Al continuar, confirmas que usarás esta plataforma con datos de práctica no identificables.
      </small>

      <!-- Acción principal para enviar las credenciales de acceso. -->
      <button class="button" type="submit">Entrar a mi cuenta <span>→</span></button>

      <!-- Enlace visual de recuperación; todavía no tiene una pantalla propia. -->
      <RouterLink class="forgot-link" to="/acceso">¿Olvidaste tu contraseña?</RouterLink>
    </form>
  </AuthLayout>
</template>
