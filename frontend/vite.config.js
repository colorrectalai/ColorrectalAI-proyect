import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  preview: {
    allowedHosts: [
      'attractive-insight-production.up.railway.app',
      'colorrectalai-production.up.railway.app',
    ],
  },
})
