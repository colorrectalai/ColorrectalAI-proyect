import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  // Pruebas unitarias y de componentes (Vitest). Las de extremo a extremo están en e2e/ (Playwright).
  test: {
    environment: 'jsdom',
    include: ['tests/unit/**/*.test.js'],
    setupFiles: ['tests/unit/setup.js'],
    restoreMocks: true,
  },
  preview: {
    allowedHosts: [
      'attractive-insight-production.up.railway.app',
      'colorrectalai-production.up.railway.app',
    ],
  },
})
