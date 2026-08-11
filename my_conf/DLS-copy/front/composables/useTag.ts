//http://localhost:8024/api/v1/tagcourses/


export const useTag = () => {
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getTag = async (id) => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/v1/tagcourses/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      //console.log('Полный ответ сервера:', response)
      //console.log(id)
  
      const tag = response.find(tag => tag.id === id);

      //console.log(tag)

      return { tag: tag.tag_name }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    getTag
  }
}

