// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],
  plugins: [
    { src: '~/plugins/pinia-persistedstate.client.ts' }
  ],

  app: {
  head: {
      title: 'СДО',
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/engs.png' }
      ]
    }
  },

  // Дополнительные настройки Tailwind (опционально)
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: '~/tailwind.config.js',
    // exposeConfig: false,
    // injectPosition: 0,
    // viewer: true,
  },
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost'
    }
  },

  ssr: true,

})
