export const useTest = () => {
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getTest = async (id) => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/test/courses/` + id + '/test/', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      //console.log('Полный ответ сервера:', response)
      //console.log(id)
  
      

      //console.log(tag)

      return { test: response, success: true }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  const sendTest = async (id, result) => {

    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/test/courses/`+id+'/submit/', {
        method: 'POST',
        body: JSON.stringify(
          {
            user_id: userId,
            course_id: id,
            quantity_correct: result
          }
        ),
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

    console.log('Полный ответ сервера:', response)
      //console.log(id)
  
      

      //console.log(tag)

      return { wrote: response }
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }

  }

  const getTestPerUser = async (id: any) => {

    if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
      console.log(authStore.user?.id, authStore.accessToken)
      throw new Error("Требуется авторизация");
    }

    const userId = authStore.user?.telegram_user_id;
    const token = authStore.accessToken;

    const response = await $fetch(`${apiBaseUrl}/api/testlist/users/${userId}/tests/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    console.log('Все тесты пользователя', response)

    if (response.tests.length === 0){
      return {test: false}
    } else {
      const test = response.tests.find(test => test.training_id === Number(id));

      return {test: test}
    }

    

  }

  return {
    getTest,
    sendTest,
    getTestPerUser
  }
}
