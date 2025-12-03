import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const baseUrl = env.VITE_API_BASE_URL || 'http://localhost:3000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler', // or 'modern'
          silenceDeprecations: ['legacy-js-api', 'color-functions', 'global-builtin', 'import'],
        },
      },
    },
    server: {
      proxy: {
        '/api': {
          target: baseUrl,
          changeOrigin: true,
        },
      },
    },
  }
})