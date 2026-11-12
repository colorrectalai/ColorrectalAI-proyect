import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
// VITE_BASE permite publicar en una subruta (GitHub Pages: /ColorrectalAI-proyect/).
export default defineConfig({
  base: process.env.VITE_BASE || '/',
  plugins: [vue()],
})
