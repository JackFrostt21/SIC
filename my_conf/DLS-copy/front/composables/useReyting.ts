import { useAuthStore } from "~/stores/auth";
import { useAuth } from "#imports";

export const useTop = () => {
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getTop = async () => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/read/users/`+ userId + '/courses/', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      //console.log('Полный ответ сервера:', response)
  
      if (!response.success) {
        throw new Error(response.message || 'Ошибка авторизации')
      }
      
      return { success: true, user: response.message }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    getCourses
  }
}
