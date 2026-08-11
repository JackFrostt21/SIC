import { useUserStore } from "~/stores/user";
import { useAuthStore } from "~/stores/auth";

export const useStat = () => {
  const userStore = useUserStore();
  const authStore = useAuthStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl

  const getStat = async () => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      //console.log(token);

      const response = await $fetch(`${apiBaseUrl}/api/v1/user-stats/user/${userId}/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log(response)

      return { success: true, stat: response };
    } catch (error: any) {
      console.error("Ошибка при получении пользователя:", error);
      return { 
        success: false, 
        message: error.message || "Произошла неизвестная ошибка" 
      };
    }
  };

  const getStatCourse = async (id: any) =>{

    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      //console.log(token);

      const response = await $fetch(`${apiBaseUrl}/api/v1/user-stats/user/${userId}/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log('what', response)

      const course = response.courses_details.find(coursee => coursee.course_id === Number(id));
      console.log('what?', course)

      return {course: course};
    } catch (error: any) {
      console.error("Ошибка при получении пользователя:", error);
      return { 
        success: false, 
        message: error.message || "Произошла неизвестная ошибка" 
      };
    }

  }
  return {
    getStat,
    getStatCourse
  };
};

//TODO доделать, засунуть в прелоад
