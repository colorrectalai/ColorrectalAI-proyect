// Punto de entrada: importa Vue, la aplicación, sus rutas y los estilos globales.
import { createApp } from 'vue'
import { RouterView } from 'vue-router'
import App from './App.vue'
import router from './router'
import './style.css'

// Crea la aplicación Vue, conecta el router y la monta en el elemento #app de index.html.
createApp(App).use(router).mount('#app')
