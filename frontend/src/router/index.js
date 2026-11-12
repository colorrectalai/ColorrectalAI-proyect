import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoadingView from '../views/LoadingView.vue'
import UploadView from '../views/UploadView.vue'
import ResultsView from '../views/ResultsView.vue'
import CompareView from '../views/CompareView.vue'
import HistoryView from '../views/HistoryView.vue'
import DetailView from '../views/DetailView.vue'

// Configuración central: relaciona cada URL con la vista que debe mostrar.
export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // Cada cambio de vista empieza al inicio de la página.
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // Zona pública y sus dos pantallas de autenticación independientes.
    { path: '/', name: 'public-home', component: HomeView },
    { path: '/inicio', name: 'dashboard', component: DashboardView },
    { path: '/acceso', name: 'login', component: LoginView },
    { path: '/registro', name: 'register', component: RegisterView },

    // Flujo de carga, análisis simulado y revisión de resultados.
    { path: '/carga', name: 'upload', component: UploadView },
    { path: '/analizando', name: 'loading', component: LoadingView },
    { path: '/resultados/:id?', name: 'results', component: ResultsView },
    { path: '/comparacion', name: 'comparison', component: CompareView },

    // Historial general y detalle de una interpretación seleccionada.
    { path: '/historial', name: 'history', component: HistoryView },
    { path: '/historial/:id', name: 'history-detail', component: DetailView },
  ],
})
