import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware((to, from, next) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken;

    console.log('refresh page', token)

    if (!token && to.path !== '/' && 
      !to.path.startsWith('/reset-password/') && 
      to.path !== '/reset-password') {
    return navigateTo('/');
  }
  });