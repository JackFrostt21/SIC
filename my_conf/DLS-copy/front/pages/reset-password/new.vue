<template>
  <div style= "background-image: url('/img/auth-bg.png')" class="bg-authbg bg-cover bg-center w-screen h-screen">

    <div class="h-[122px]"></div>
    <img src="../../public/img/eng-logo.png" class="mx-auto">

    <div class="w-[90%] sm:w-[514px] h-[315px] sm:h-[405px] mt-[21px] rounded-[20px] bg-white shadow-[0px_0px_100px_0px_rgba(0,0,0,0.1)] mx-auto relative">

      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 relative h-full w-[81%] sm:w-full">

      <h1 class="absolute top-[16px] sm:top-[30px] sm:left-[31.21px] sm:w-[405.79px] h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black">
        Новый пароль
      </h1>

      <input
          id="inputPassword"
          type="text"
          v-model="new_password"
          class="absolute sm:w-[451px] w-[100%] h-[32px] top-[54px] sm:h-[46px] sm:top-[76px] sm:left-[31px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
      />

      <p class="absolute top-[104px] sm:top-[136px] sm:left-[31px] w-[100%] sm:w-[451px] h-[54px] font-sans text-[12px]
      sm:text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]">
      Пароль должен соответствовать формату. Используйте 8 и более символов: латинские буквы (a-z) и минимум одну цифру.
      </p>

      <h1 class="absolute top-[154px] sm:top-[210px] sm:left-[31.21px] sm:w-[405.79px] h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black">
        Повторите пароль
      </h1>

      <input
          id="inputPassword"
          type="text"
          v-model="confrim_password"
          class="absolute w-[100%] h-[32px] top-[194px] sm:w-[451px] sm:h-[46px] sm:top-[260px] sm:left-[31px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
      />

      <div @click="handleReset" class="w-[100%] h-[32px] top-[244px] sm:w-[451px] sm:h-[53px] absolute sm:top-[322px] sm:left-[31px] rounded-[10px] px-[80px] py-[17px] bg-[#0C1E45] 
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
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { useResetStore } from '#imports';
import { useReset } from '#imports';

const resetStore = useResetStore();
const router = useRouter();
const sendReset = useReset();

const new_password = ref('');
const confrim_password = ref('');
const token = resetStore.token;

const handleReset = async () =>{
  const feedback = await sendReset.getReset(token, new_password.value, confrim_password.value);

  if (feedback.success){
    router.push('/reset-password/done')
  } else {
    router.push('/reset-password/confrim')
  }
}


</script>

<style>

</style>