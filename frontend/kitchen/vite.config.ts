import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "/kitchen/" : "/",
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://backend:80',
        changeOrigin: true,
      },
      '/agent': {
        target: 'http://agent:8001',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/agent/, ''),
      },
      '/stt': {
        target: 'http://stt:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/stt/, ''),
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
