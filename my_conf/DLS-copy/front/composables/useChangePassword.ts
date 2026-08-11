import { useAuthStore } from "~/stores/auth";
import { useAuth } from "#imports";

export const useChangePassword = () => {
  const authStore = useAuthStore();
  const refresh = useAuth();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const change = async (credentials: {password: string}) => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      console.log(credentials)

      const response = await $fetch(`${apiBaseUrl}/api/auth/password/change/`, {
        method: 'POST',
        body: JSON.stringify({
          old_password: authStore.password,
          new_password: credentials.password,
          confirm_password: credentials.password
        }),
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)
  
      if (!response.success) {
        throw new Error(response.message || 'Ошибка авторизации')
      }

      const feedback = await refresh.login({
        login: authStore.login,
        password: credentials.password
      })
      
      return { success: true, user: response.message }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    change
  }
}

