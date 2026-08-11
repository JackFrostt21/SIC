import { useAuthStore } from "~/stores/auth";

export const useAuth = () => {
  const authStore = useAuthStore()

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const login = async (credentials: { login: string; password: string }) => {
    try {
      console.log(credentials)
      const response = await $fetch(`${apiBaseUrl}/api/auth/login/`, {
        method: 'POST',
        body: JSON.stringify({
          login: credentials.login, 
          password: credentials.password,
        }),
        headers: {
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)
  
      if (!response.success) {
        throw new Error(response.message || 'Ошибка авторизации')
      }

  
      console.log('Токены:', 'a: ', response.access_token, 'r: ', response.refresh_token)
      authStore.setTokens(response.access_token, response.refresh_token)

      console.log("Access Token:", authStore.accessToken)
      console.log("Refresh Token:", authStore.refreshToken)

      authStore.setUser({
        email: response.user.email,
        id: response.user.id,
        username: response.user.username,
        full_name: response.user.full_name,
        phone: response.user.phone,
        telegram_user_id: response.user.telegram_user_id
      });

      authStore.setPassword(credentials.password, credentials.login);
      
      // Проверка
      console.log("User:", authStore.user);
      
      return { success: true, user: response.user }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    isAuthenticated: computed(() => authStore.isAuthenticated),
    user: computed(() => authStore.user),
    login,
    logout: authStore.clearAuth
  }
}
