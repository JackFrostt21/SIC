import { useAuthStore } from "~/stores/auth"

export default defineNuxtPlugin((nuxtApp) => {
    const authStore = useAuthStore()
  
    const $api = $fetch.create({
      baseURL: 'http://localhost:8024/api',
      async onRequest({ options }) {
        if (authStore.accessToken) {
          options.headers = {
            ...options.headers,
            Authorization: `Bearer ${authStore.accessToken}`
          }
        }
      },
      async onResponseError({ response }) {
        if (response.status === 401) {
          await authStore.clearAuth()
          navigateTo('/')
        }
      }
    })
  
    return { provide: { api: $api } }
  })
