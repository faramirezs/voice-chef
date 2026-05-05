import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        // Note: MP. This tells the Vite (in frontend container)
        // to forward the request to your backend URL.
        target: 'http://backend:80',
        // Note: MP. The rewrite function path.replace(/^\/api/, '') 
        // removes /api from the beginning of the path.
        // Example: Vite proxy forwards the request to http://your_backend_URL/tables
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // '/api/uploads': {
      //   target: 'http://backend:80',
      //   changeOrigin: true,
      // },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
