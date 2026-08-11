<template>
  <div>
    <div
      class="w-[90%] h-[280px] sm:w-[514px] sm:h-[385px] mt-[21px] rounded-[20px] bg-white shadow-[0px_0px_100px_0px_rgba(0,0,0,0.1)] mx-auto relative"
    >
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 relative h-full w-[81%] sm:w-full">
      <h1
        class="absolute top-[6%] sm:top-[30px] sm:left-[31.21px] sm:w-[405.79px] sm:h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black"
      >
        Вход в учебный портал
      </h1>

      <div class="absolute w-[100%] sm:top-[80px] sm:left-[31.21px] sm:w-[460px] sm:h-[83px] top-[20%]">
        <div class="w-[49px] h-[22px] flex items-center">
          <span v-if="success" class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]"
            >Логин</span
          >
          <span v-else class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#D21E41]"
            >Логин</span
          >
        </div>

        <form @submit.prevent="handleLogin">
          <input
            v-if="success"
            id="inputLogin"
            v-model="login"
            type="text"
            class="w-[100%] h-[35px] sm:w-[451px] sm:h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] text-black bg-[#E6E6E6] not-placeholder-shown:bg-white focus:outline-none focus:ring-1 focus:ring-[#909090]"
          />
          <input
            v-else
            id="inputLogin"
            v-model="login"
            type="text"
            class="w-[100%] h-[35px] sm:w-[451px] sm:h-[46px] mt-[6px] rounded-[10px] border border-[#D21E41] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] text-black not-placeholder-shown:bg-white focus:outline-none focus:ring-1 focus:ring-[#D21E41]"
          />
        </form>
      </div>

      <div class="absolute w-[100%] top-[45%] sm:top-[169px] sm:left-[31.21px] sm:w-[460px] sm:h-[75px]">
        <div class="w-[49px] h-[22px] flex items-center">
          <span v-if="success" class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]"
            >Пароль</span>
            <span v-else class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#D21E41]"
            >Пароль</span>
        </div>

        <div class="relative">
          <form @submit.prevent="handleLogin">
            <input
              v-if="success"
              id="inputPassword"
              v-model="password"
              :type="visible ? 'text' : 'password'"
              class="w-[100%] h-[35px] sm:w-[451px] sm:h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[45px] pb-[17px] pl-[20px] gap-[10px] text-black bg-[#E6E6E6] not-placeholder-shown:bg-white focus:outline-none focus:ring-1 focus:ring-[#909090]"
            />
            <input
              v-else
              id="inputPassword"
              v-model="password"
              :type="visible ? 'text' : 'password'"
              class="w-[100%] h-[35px] sm:w-[451px] sm:h-[46px] mt-[6px] rounded-[10px] border border-[#D21E41] pt-[17px] pr-[45px] pb-[17px] pl-[20px] gap-[10px] text-black not-placeholder-shown:bg-white focus:outline-none focus:ring-1 focus:ring-[#D21E41]"
            />
          </form>

          <img
            v-if="visible"
            src="../public/img/eye-on.png"
            @click="toggleHidePassword"
            class="absolute top-[33%] left-[90%] sm:top-[17px] sm:left-[409.79px] transform cursor-pointer"
          />
          <img
            v-else
            src="../public/img/eye-off.png"
            @click="toggleHidePassword"
            class="absolute top-[33%] left-[90%] sm:top-[17px] sm:left-[409.79px] transform cursor-pointer"
          />
        </div>
      </div>

      <div
        v-if="rememberMe"
        class="absolute w-[18px] h-[18px] top-[71%] sm:top-[250px] sm:left-[31px] sm:w-[22.89px] sm:h-[22px] rounded-[5px] border border-[#8A8A8A] relative cursor-pointer"
        @click="toggleRememberPassword"
      >
        <img
          src="../public/img/r-password.svg"
          class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
        />
      </div>

      <div
        v-else
        class="absolute w-[18px] h-[18px] top-[71%] sm:top-[250px] sm:left-[31px] sm:w-[22.89px] sm:h-[22px] rounded-[5px] border border-[#8A8A8A] relative cursor-pointer"
        @click="toggleRememberPassword"
      ></div>

      <h1
        class="text-[12px] top-[72%] left-[8%] sm:w-[135.26px] sm:h-[19px] absolute sm:top-[254px] sm:left-[62.43px] font-sans font-normal sm:text-[14px] leading-none text-black"
      >
        Запомнить пароль
      </h1>

      <NuxtLink
        to="/reset-password/"
        class="absolute text-[12px] right-0 top-[72%] sm:top-[254px] sm:left-[327.79px] w-fit h-[19px] font-sans font-semibold sm:text-[14px] leading-none underline decoration-solid underline-offset-0 decoration-0 text-[#0C1E45]"
      >
        Восстановить пароль
      </NuxtLink>

      <button
        @click="handleLogin"
        :disabled="isLoading"
        class="w-[100%] h-[32px] top-[82%] sm:w-[451px] sm:h-[53px] absolute sm:top-[302px] sm:left-[31px] rounded-[10px] px-[80px] py-[17px] bg-[#0C1E45] text-white flex items-center justify-center gap-[10px] transition-colors duration-100 hover:bg-[#3D4B6A] active:bg-[#8A8A8A] disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        <span v-if="!isLoading" class="font-sans font-semibold text-base leading-none tracking-[0%]">
          Войти
        </span>
        <span v-else class="loading"></span>
      </button>

      <p v-if="!success" class="absolute top-[360px] left-[31px] text-[#D21E41] text-sm">
        Проверьте корректность введенных данных.
      </p>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'
import { useStorage } from '@vueuse/core'

let success = true

const authStore = useAuth()
const router = useRouter()

// Состояние компонента с useStorage
const visible = ref(false)
const login = useStorage('login', '')
const password = useStorage('password', '')
const rememberMe = useStorage('rememberMe', false)
const error = ref('')
const isLoading = ref(false)

// Методы
const toggleRememberPassword = () => {
  rememberMe.value = !rememberMe.value
}

const toggleHidePassword = () => {
  visible.value = !visible.value
}

onMounted(() => {
  if (rememberMe.value) {
    // Значения уже подхватятся из useStorage автоматически
  } else {
    // Очищаем если не выбрано "запомнить меня"
    login.value = ''
    password.value = ''
  }
})

const handleLogin = async () => {
  if (!login.value || !password.value) {
    error.value = 'Пожалуйста, заполните все поля'
    return
  }

  try {
    isLoading.value = true
    error.value = ''
    
    const feedback = await authStore.login({
      login: login.value,
      password: password.value,
      remember: rememberMe.value
    })

    console.log('feedback: ', feedback)
    
    if (feedback.success) {
      router.push('/sdo')
      // Если не выбрано "запомнить меня" - очищаем
      if (!rememberMe.value) {
        login.value = ''
        password.value = ''
      }
    } else {
      success = false
    }
    
    console.log({
      login: login.value,
      password: password.value,
      rememberMe: rememberMe.value
    })
    
  } catch (err) {
    success = false
  } finally {
    isLoading.value = false
  }
}
</script>

<style>
.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>