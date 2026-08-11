export const useTopics = () => {
  const authStore = useAuthStore();
  const topicStore = useCoursesStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getTopics = async (courseId: any) => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/v1/coursetopics/course/`+courseId+'/user/'+userId+'/', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)

      topicStore.setTopics(response);



      //console.log('топики', topicStore.topics);
      
      return { topics: response}
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    getTopics
  }
}