import { useUserStore } from "~/stores/user";
import { useAuthStore } from "~/stores/auth";

export const useUser = () => {
  const userStore = useUserStore();
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl

  const getUser = async () => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      //console.log(token);

      const response = await $fetch(`${apiBaseUrl}/api/v1/telegramusers/${userId}/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log(response)

      if (!response) {
        throw new Error(response?.message || "Не удалось получить данные пользователя");
      }

      if (response.image){

      userStore.setUser(
        response.is_actual,
        response.state,
        response.full_name,
        response.last_name,
        response.first_name,
        response.middle_name,
        response.date_of_birth,
        response.email,
        response.phone,
        response.language,
        response.image,
        response.company,
        response.departament,
        response.job_title
      );

    } else {

      userStore.setUser(
        response.is_actual,
        response.state,
        response.full_name,
        response.last_name,
        response.first_name,
        response.middle_name,
        response.date_of_birth,
        response.email,
        response.phone,
        response.language,
        'https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg',
        response.company,
        response.departament,
        response.job_title
      );

    }

      return { success: true, user: response };
    } catch (error: any) {
      console.error("Ошибка при получении пользователя:", error);
      return { 
        success: false, 
        message: error.message || "Произошла неизвестная ошибка" 
      };
    }
  };

  return {
    getUser,
    user: computed(() => userStore.state),
  };
};

//TODO доделать, засунуть в прелоад