export const useReset = () => {

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getReset = async (token: string, new_password: string, confrim_password: string) => {
    try {
      const response = await $fetch(`${apiBaseUrl}/api/auth/password/reset/confirm/`, {
        method: 'POST',
        body: JSON.stringify({
            token: token,
            new_password: new_password,
            new_password_confirm: confrim_password}),
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
    getReset
  }
}

