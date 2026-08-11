import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    password: null as string | null,
    login: null as string | null,
    user: null as {email: string; id: string; username: string, full_name: string, phone: string, telegram_user_id: string} | null
  }),
  actions: {
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
    },
    clearAuth() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
    },
    setUser(userData: {
      email: string; id: string; username: string, full_name: string, phone: string, telegram_user_id: string
    }) {
      this.user = userData;
    },
    async refreshToken() {
      // Логика обновления токена
    },
    setPassword(password: string, login: string){
      this.password = password
      this.login = login
    }
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken
  },
  persist: true,
})
