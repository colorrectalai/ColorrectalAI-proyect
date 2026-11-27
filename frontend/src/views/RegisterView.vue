<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Eye, EyeOff } from '@lucide/vue'
import AuthLayout from '../components/AuthLayout.vue'
import { registrarUsuario } from '../api'
import { guardarSesion } from '../userProfile'

const router = useRouter()
// Datos escritos por la persona durante la creación de su perfil.
const name = ref('')
const email = ref('')
const userType = ref('')
const password = ref('')
const confirmPassword = ref('')
// Cada campo de contraseña controla su propia visibilidad.
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const legalAccepted = ref(false)
const error = ref('')
// Evita crear la cuenta dos veces mientras el servidor responde.
const sending = ref(false)

// Comprueba los campos y crea la cuenta en el servidor (la contraseña se guarda con hash).
async function submit() {
  error.value = ''

  if (!name.value || !email.value || !userType.value || !password.value || !confirmPassword.value) {
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

  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }

  sending.value = true
  try {
    guardarSesion(await registrarUsuario({
      nombre: name.value,
      correo: email.value,
      tipoUsuario: userType.value,
      contrasena: password.value,
      aceptaAviso: legalAccepted.value,
    }))
    router.push('/inicio')
  } catch (e) {
    error.value = e.message
  } finally {
    sending.value = false
  }
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

      <!-- Tipo de usuario declarado para el perfil académico. -->
      <label class="auth-field">
        Tipo de usuario
        <select v-model="userType" name="userType" required>
          <option value="" disabled>Selecciona una opción</option>
          <option value="Estudiante">Estudiante</option>
          <option value="Profesional">Profesional</option>
          <option value="Otro">Otro</option>
        </select>
      </label>

      <!-- Contraseña nueva; el navegador solicita al menos ocho caracteres. -->
      <div class="auth-field">
        <label for="register-password">Contraseña</label>
        <span class="password-input-wrap">
          <input
            id="register-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            placeholder="Mínimo 8 caracteres"
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

      <!-- Campo separado que permite comprobar que ambas contraseñas coincidan. -->
      <div class="auth-field">
        <label for="confirm-password">Confirmar contraseña</label>
        <span class="password-input-wrap">
          <input
            id="confirm-password"
            v-model="confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            autocomplete="new-password"
            placeholder="Vuelve a escribir tu contraseña"
            minlength="8"
            required
          />
          <button
            class="password-visibility-toggle"
            type="button"
            :aria-label="showConfirmPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            :aria-pressed="showConfirmPassword"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <EyeOff v-if="showConfirmPassword" :size="18" aria-hidden="true" />
            <Eye v-else :size="18" aria-hidden="true" />
          </button>
        </span>
      </div>

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
      <button class="button" type="submit" :disabled="sending">{{ sending ? 'Creando la cuenta…' : 'Crear mi cuenta' }} <span>→</span></button>
    </form>
  </AuthLayout>
</template>

<style scoped>
/* Agrupa cada contraseña con su botón del ojo dentro del alto existente del campo. */
.password-input-wrap {
  position: relative;
  display: block;
  margin-top: 8px;
}

/* Deja espacio para el icono en el extremo derecho del campo. */
.auth-form :deep(.auth-field .password-input-wrap input) {
  margin-top: 0;
  padding-right: 46px;
}

/* Botón accesible para alternar la visibilidad de cada contraseña. */
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
