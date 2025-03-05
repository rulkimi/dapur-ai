import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueRouter from 'unplugin-vue-router/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    VueRouter(), 
    vue(),
    VitePWA({ 
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      }
    })
  ],
})
