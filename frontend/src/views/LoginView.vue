<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Eye, EyeOff } from '@lucide/vue'
import AuthLayout from '../components/AuthLayout.vue'
import { iniciarSesion } from '../api'
import { guardarSesion } from '../userProfile'

const router = useRouter()
// Valores controlados por v-model en los campos del formulario.
const email = ref('')
const password = ref('')
// Alterna la visibilidad de la contraseña sin cambiar su valor.
const showPassword = ref(false)
// Mensaje de validación o del servidor que se muestra debajo de los campos.
const error = ref('')
// Evita enviar dos veces mientras el servidor responde.
const sending = ref(false)

// Valida que haya datos y comprueba el correo y la contraseña en el servidor.
async function submit() {
  error.value = ''

  if (!email.value || !password.value) {
    error.value = 'Completa tu correo y contraseña para continuar.'
    return
  }

  sending.value = true
  try {
    guardarSesion(await iniciarSesion({ correo: email.value, contrasena: password.value }))
    router.push('/inicio')
  } catch (e) {
    error.value = e.message
  } finally {
    sending.value = false
  }
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
      <div class="auth-field">
        <label for="login-password">Contraseña</label>
        <span class="password-input-wrap">
          <input
            id="login-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            placeholder="Tu contraseña"
            minlength="8"
            required
          />
          <button
            class="password-visibility-toggle"
            type="button"
            :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" :size="18" aria-hidden="true" />
            <Eye v-else :size="18" aria-hidden="true" />
          </button>
        </span>
      </div>

      <!-- Mensaje de validación si faltan datos. -->
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <!-- Aviso de uso de datos de práctica. -->
      <small class="form-legal">
        Al continuar, confirmas que usarás esta plataforma con datos de práctica no identificables.
      </small>

      <!-- Acción principal para enviar las credenciales de acceso. -->
      <button class="button" type="submit" :disabled="sending">{{ sending ? 'Verificando…' : 'Entrar a mi cuenta' }} <span>→</span></button>

      <!-- Enlace visual de recuperación; todavía no tiene una pantalla propia. -->
      <RouterLink class="forgot-link" to="/acceso">¿Olvidaste tu contraseña?</RouterLink>
    </form>
  </AuthLayout>
</template>

<style scoped>
/* Agrupa el campo y el botón del ojo sin alterar el alto original del formulario. */
.password-input-wrap {
  position: relative;
  display: block;
  margin-top: 8px;
}

/* Deja espacio para el icono dentro del extremo derecho del campo. */
.auth-form :deep(.auth-field .password-input-wrap input) {
  margin-top: 0;
  padding-right: 46px;
}

/* Botón accesible para alternar entre texto visible y contraseña oculta. */
.password-visibility-toggle {
  position: absolute;
  top: 50%;
  right: 10px;
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  padding: 0;
  transform: translateY(-50%);
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}

.password-visibility-toggle:hover {
  background: var(--brand-soft);
  color: var(--brand);
}

.password-visibility-toggle:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 1px;
}
</style>
