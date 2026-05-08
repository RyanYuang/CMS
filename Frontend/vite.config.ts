import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/cms/leowong/',
  server: {
    port: 5173,
    proxy: {
      // 本地开发默认后端在 18000；可通过 VITE_API_PROXY_TARGET 覆盖
      '/api': { target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:18000', changeOrigin: true },
      '/static': { target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:18000', changeOrigin: true },
    },
  },
})
