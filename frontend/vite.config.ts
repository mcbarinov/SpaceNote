import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.SPACENOTE_SPA_PORT || '3001'),
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})