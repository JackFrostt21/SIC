<template>
  <div class="md:w-[1040px] w-[90%] h-[138px] rounded-[10px] bg-white mx-auto relative">
  
    <span class="absolute left-[20px] top-[20px] md:w-[69px] h-[25px] font-semibold text-[18px] leading-[1] tracking-[0px] text-black font-open-sans">
      Группы
    </span>

    <div class="absolute left-[20px] top-[62px] flex flex-row md:w-[301px] h-[22px] gap-[47px]">
      
      <span class="md:w-[109px] h-[22px] md:text-[16px] text-[14px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Департамент
      </span>

      <span class="md:w-[145px] h-[22px] font-open-sans font-semibold md:text-[16px] text-[14px] leading-[16px] text-black">
        {{ departament }}
      </span>

    </div>

    <div class="absolute left-[20px] top-[96px] flex flex-row md:w-[301px] h-[22px] gap-[47px]">
      
      <span class="md:w-[109px] h-[22px] md:text-[16px] text-[14px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Должность
      </span>

      <span class="md:w-[145px] h-[22px] font-open-sans font-semibold md:text-[16px] text-[14px] leading-[16px] text-black">
        {{ job_title }}
      </span>

    </div>

    <!--div class="absolute left-[20px] top-[130px] flex flex-row w-[301px] h-[22px] gap-[47px]">
      
      <span class="w-[109px] h-[22px] text-[16px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Категория
      </span>

      <span class="w-[145px] h-[22px] font-open-sans font-semibold text-[16px] leading-[16px] text-black">
        Руководитель
      </span>

    </div>

    <div class="absolute left-[20px] top-[164px] flex flex-row w-[301px] h-[22px] gap-[47px]">
      
      <span class="w-[109px] h-[22px] text-[16px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Команда
      </span>

      <span class="w-[145px] h-[22px] font-open-sans font-semibold text-[16px] leading-[16px] text-black">
        Демо
      </span>

    </div>

    <div class="absolute left-[20px] top-[198px] flex flex-row w-[301px] h-[22px] gap-[47px]">
      
      <span class="w-[109px] h-[22px] text-[16px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Назначение
      </span>

      <span class="w-[145px] h-[22px] font-open-sans font-semibold text-[16px] leading-[16px] text-black">
        Администраторы
      </span>

    </div>

    <div class="absolute left-[20px] top-[232px] flex flex-row w-[301px] h-[22px] gap-[47px]">
      
      <span class="w-[109px] h-[22px] text-[16px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Роль
      </span>

      <span class="w-[145px] h-[22px] font-open-sans font-semibold text-[16px] leading-[16px] text-black">
        Создатель курса
      </span>

    </div>

    <div class="absolute left-[20px] top-[266px] flex flex-row w-[301px] h-[22px] gap-[47px]">
      
      <span class="w-[109px] h-[22px] text-[16px] leading-[16px] font-semibold text-[#8A8A8A] font-open-sans">
        Страна
      </span>

      <span class="w-[145px] h-[22px] font-open-sans font-semibold text-[16px] leading-[16px] text-black">
        Россия
      </span>

    </div-->

  </div>
</template>

<script>

import { useAuthStore } from '@/stores/auth';

export default {
  computed: {
    departament() {
      return useUserStore().departament;
    },
    job_title() {
      return useUserStore().job_title;
    }
    // TODO: категория, команда, назначение, роль
  }
}

</script>


<style>

</style>