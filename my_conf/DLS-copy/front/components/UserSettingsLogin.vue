<template>
  <div class="md:w-[515px] w-full h-[116px] rounded-[10px] bg-white relative">

    <span class="md:w-[509.5px] h-[25px] font-semibold md:text-[18px] text-[16px] leading-[1] tracking-[0] text-black top-[20px] left-[20px] font-sans absolute" >
      Логин
    </span>

    <span class="md:w-[169px] h-[18px] font-medium md:text-[16px] text-[14px] leading-[1.15] text-black absolute left-[20px] top-[52px]" style="font-family: 'Inter', sans-serif;">
      {{ userStore.login }}
    </span>

    <span class="md:w-[428px] h-[19px] font-semibold md:text-[14px] text-[12px] leading-[1] tracking-normal text-[#8A8A8A] absolute left-[20px] top-[80px] font-sans">
      Чтобы изменить эти данные, обратитесь к администратору
    </span>
    
  </div>
</template>

<script lang="ts" setup>
import { useAuthStore } from '#imports';

const userStore = useAuthStore();

</script>

<style>

</style>