import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Smart Campus Sustainability Engine',
        short_name: 'CarbonEngine',
        description: 'Real-time CO₂e tracking & AI-driven reduction strategies.',
        theme_color: '#0f172a',
        background_color: '#0f172a'
      }
    })
  ],
})
