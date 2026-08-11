import { useUserStore } from "~/stores/user";
import { useAuthStore } from "~/stores/auth";
import type { formatDate } from "@vueuse/core";

export const useAvatar = () => {
  const userStore = useUserStore();
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl

  const setAva = async (image: File) => {
    try {
      if (!authStore.accessToken) {
        console.log(authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const token = authStore.accessToken;

      console.log(token);

      console.log('Вход: ', image)


       // Создаем FormData объект
    const formData = new FormData();
    formData.append("avatar", image);

    const response = await $fetch(`${apiBaseUrl}/api/auth/avatar/`, {
      method: "PUT",
      body: formData, // Используем FormData вместо JSON объекта
      headers: {
        Authorization: `Bearer ${token}`
        // НЕ устанавливаем Content-Type - браузер сам установит multipart/form-data с boundary
      },
    });


      console.log('Полный ответ сервера: ', response.body)

      console.log('url ava from store:', userStore.image);

      userStore.setAvatar(response.avatar_url);

      console.log('url ava from store:', userStore.image)

      if (!response) {
        throw new Error(response?.message || "Не удалось получить данные пользователя");
      }

      

      return { success: true, data: response };
    } catch (error: any) {
      console.error("Ошибка при получении пользователя:", error);
      return { 
        success: false, 
        message: error.message || "Произошла неизвестная ошибка" 
      };
    }
  };

  return {
    setAva,
    success: true
  };
};
