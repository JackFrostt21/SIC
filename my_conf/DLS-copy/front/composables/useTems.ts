export const useTems = () => {
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getTems = async () => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/v1/coursedirections/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      //console.log('Полный ответ сервера:', response)
      //console.log(id)

      //console.log(tag)

      return { tems: response }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  const readTems = async (course_id, topic_id) => {

    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/read/users/`+userId+'/courses/'+course_id+'/topics/'+topic_id+'/mark-read/', {
        method: 'POST',
        body: JSON.stringify({  // Явное преобразование в JSON строку
          is_read: true
        }),
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)
      //console.log(id)

      //console.log(tag)

      return { tems: response }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }

  }

  return {
    getTems,
    readTems
  }
}