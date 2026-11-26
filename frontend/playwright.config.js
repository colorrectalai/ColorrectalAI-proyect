// Pruebas de extremo a extremo: el frontend compilado en navegadores reales, con la API simulada
// (mismo contrato que la API real) para probar flujos, errores y diseño sin depender del servidor.
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: 'e2e',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['junit', { outputFile: 'e2e-resultados.xml' }]],
  use: { baseURL: 'http://localhost:4173', viewport: { width: 1366, height: 768 } },
  webServer: {
    command: 'VITE_API_URL=http://api.prueba npm run build && npx vite preview --port 4173 --strictPort',
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    { name: 'chrome', use: { ...devices['Desktop Chrome'], viewport: { width: 1366, height: 768 } } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'], viewport: { width: 1366, height: 768 } } },
    { name: 'edge', use: { ...devices['Desktop Edge'], channel: 'msedge', viewport: { width: 1366, height: 768 } } },
  ],
})
