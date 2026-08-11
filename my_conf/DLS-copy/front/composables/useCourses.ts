import { useAuthStore } from "~/stores/auth";
import { useCoursesStore } from "#imports";
import { useAuth } from "#imports";

function sortByObligatory(courses: any[]): [any[], any[]] {
  const obligatoryTrue = courses.filter(course => course.obligatory === true);
  const obligatoryFalse = courses.filter(course => course.obligatory === false);
  return [obligatoryTrue, obligatoryFalse];
}

function sortByCompleted(courses: any[]): [any[], any[]] {
  const completeTrue = courses.filter(course => course.is_completed == true);
  const completeFalse = courses.filter(course => course.is_completed === false);
  return [completeTrue, completeFalse]
}

export const useCourses = () => {
  const authStore = useAuthStore();
  const coursesStore = useCoursesStore();

  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  
  const getCourses = async () => {
    try {
      if (!authStore.user?.telegram_user_id || !authStore.accessToken) {
        console.log(authStore.user?.id, authStore.accessToken)
        throw new Error("Требуется авторизация");
      }

      const userId = authStore.user?.telegram_user_id;
      const token = authStore.accessToken;

      const response = await $fetch(`${apiBaseUrl}/api/v1/trainingcourses/user/`+userId+'/', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      console.log('Полный ответ сервера:', response)

      coursesStore.setCourses(response);
  
      const [mandatoryCourses, optionalCourses] = sortByObligatory(response);

      console.log("Обязательные курсы:", mandatoryCourses);
      console.log("Опциональные курсы:", optionalCourses);
      
      return { nessary: mandatoryCourses, all: response, notCompleted: response}
    } catch (error) {
      console.error('Ошибка входа:', error)
      return { success: false, message: error.message }
    }
  }

  return {
    getCourses
  }
}
