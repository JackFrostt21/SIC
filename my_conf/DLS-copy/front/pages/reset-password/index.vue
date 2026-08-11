<template>
  <div style= "background-image: url('/img/auth-bg.png')" class="bg-cover bg-center w-screen h-screen">

    <div class="h-[122px]"></div>
    <img src="../../public/img/eng-logo.png" class="mx-auto">

    <div class="w-[90%] h-[200px] sm:w-[514px] sm:h-[281px] mt-[21px] rounded-[20px] bg-white shadow-[0px_0px_100px_0px_rgba(0,0,0,0.1)] mx-auto relative">

      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 relative h-full w-[81%] sm:w-full">

      <h1 class="absolute top-[16px] sm:top-[30px] sm:left-[31.21px] sm:w-[405.79px] h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black">
        Восстановление пароля
      </h1>

      <p class="absolute top-[54px] w-[100%] sm:top-[76px] sm:left-[31px] sm:w-[451px] sm:h-[36px] font-sans text-[12px]
      sm:text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]">
      Введите номер телефона или email, указанный при регистрации
      </p>

      <input
          id="inputContact"
          type="text"
          v-model="email"
          class="absolute top-[95px] w-[100%] h-[32px] sm:w-[451px] sm:h-[46px] sm:top-[120px] sm:left-[31px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
      />

      <div @click="handleAttempt" class="top-[149px] h-[32px] w-[100%] sm:w-[451px] sm:h-[53px] absolute sm:top-[198px] sm:left-[31px] rounded-[10px] px-[80px] py-[17px] bg-[#0C1E45] 
      text-white flex items-center justify-center gap-[10px] transition-colors duration-100 hover:bg-[#3D4B6A] active:bg-[#8A8A8A]">

          <h1 class="w-[51px] h-[22px] font-sans font-semibold text-base leading-none tracking-[0%] text-center">
            Далее
          </h1>

        </div>
        </div>      
    </div>
  </div>    
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useRequest } from '#imports';
import { useResetStore } from '#imports';

const resetAttempt = useRequest();
const email = ref('');
const router = useRouter();
const resetStore = useResetStore();

const handleAttempt = async () => {
  if (!email.value) {
    console.log('Пожалуйста, заполните все поля')
    return
  }

  resetStore.setEmail(email);
  console.log('store email:', resetStore.email)

  try {
    const feedback = await resetAttempt.getRequest(email.value)

    console.log('feedback: ', feedback)

    router.push('/reset-password/confrim')
    
  } catch (err) {
    console.log(err)
  }
}


</script>

<style>

</style>