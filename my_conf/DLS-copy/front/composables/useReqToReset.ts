export const useRequest = () => {

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getRequest = async (email: string) => {
    try {
      const response = await $fetch(`${apiBaseUrl}/api/auth/password/reset/`, {
        method: 'POST',
        body: JSON.stringify({
          email: email,
        }),
        headers: {
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)
  
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
    getRequest
  }
}
