import { readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(path.join(__dirname, 'package.json'), 'utf-8')) as { version?: string }
const appVersion = typeof pkg.version === 'string' ? pkg.version : '0.0.0'
const buildTimeIso = new Date().toISOString()

// https://vite.dev/config/
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(appVersion),
    __BUILD_TIME__: JSON.stringify(buildTimeIso),
  },
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
