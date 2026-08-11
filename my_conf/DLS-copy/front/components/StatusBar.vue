<template>
  <div class="h-auto sm:w-[1038px] sm:h-[22px] mx-auto relative">

    <p class=" w-[134px] h-[22px] font-semibold text-[16px] leading-[100%] tracking-[0%] text-black font-sans top-0 hidden md:block">Мои результаты</p>

    <div v-if="isOpen" @click="toggleOpen" class="md:hidden block bg-white rounded-[10px] w-[249px] h-[32px] flex">

      <p class="font-semibold text-[14px] leading-[100%] tracking-[0%] text-black font-sans my-auto ml-[23%]">Мои результаты</p>

      <img 
        v-if="!isOpen" 
        src="../public/img/vector_up.svg" 
        class="ml-[3%] w-[15px] h-[9px] my-auto"
      />
      <img 
        v-if="isOpen" 
        src="../public/img/vector.svg" 
        class="ml-[3%] w-[15px] h-[9px] my-auto"
      />

    </div>

    <div v-if="!isOpen" @click="toggleOpen" class="md:hidden block bg-white rounded-[10px] w-[249px] h-[137px] z-50 relative">

      <div class="flex relative w-full h-[32px]">
        <p class="font-semibold text-[14px] leading-[100%] tracking-[0%] text-black font-sans my-auto ml-[23%]">Мои результаты</p>

        <img 
          v-if="!isOpen" 
          src="../public/img/vector_up.svg" 
          class="ml-[3%] w-[15px] h-[9px] my-auto"
        />
      </div>

      <div class="w-auto max-w-[223px] flex flex-col mt-[5%] mb-[5%] mx-auto gap-[7px]">

        <div class="h-[22px] top-[0px]  relative">

          <p class="w-[42px] h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Тесты</p>

          <p class="whitespace-nowrap w-fit h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[60px]"> {{feedback.stat.summary.passed_tests}} из {{feedback.stat.summary.total_tests}} пройдено</p>

        </div>

        <div class="w-fit h-[22px] top-[0px] relative">

          <p class="w-[56px] h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Темы</p>

          <p class="whitespace-nowrap w-fit h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[65px]">{{feedback.stat.summary.read_topics}} из {{feedback.stat.summary.total_topics}} пройдено</p>

        </div>

        <div class="w-fit h-[22px] top-[0px] relative">

          <p class="w-[81px] h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Курсы</p>

          <p class="whitespace-nowrap w-fit h-[22px] font-semibold text-[14px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[70px] top-[0px]">{{feedback.stat.summary.completed_courses}} из {{feedback.stat.summary.total_courses}} пройдено</p>

        </div>

      </div>

    </div>


    <div class="flex flex-row h-[22px] gap-[52px] absolute top-[0px] left-[345px] w-[723px] hidden md:flex">

    <div class="w-[190px] h-[22px] top-[0px]  relative">

      <p class="w-[48px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Тесты</p>

      <p class="w-[130px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[60px]"> {{feedback.stat.summary.passed_tests}} из {{feedback.stat.summary.total_tests}} пройдено</p>

    </div>

    <div class="w-[206px] h-[22px] top-[0px] relative">

      <p class="w-[64px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Темы</p>

      <p class="w-[130px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[65px]">{{feedback.stat.summary.read_topics}} из {{feedback.stat.summary.total_topics}} пройдено</p>

    </div>

    <div class="w-[223px] h-[22px] top-[0px] relative">

      <p class="w-[81px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-black font-sans absolute top-[0px]">Курсы</p>

      <p class="w-[130px] h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-[#8A8A8A] absolute left-[70px] top-[0px]">{{feedback.stat.summary.completed_courses}} из {{feedback.stat.summary.total_courses}} пройдено</p>

    </div>

  </div>

    
  </div>
</template>

<script setup>

import { useStat } from '#imports';

const stat = useStat();

const feedback = await stat.getStat();

console.log(feedback);
const isOpen = ref(false);

const toggleOpen = () => {
  isOpen.value = !isOpen.value;
};
</script>

<style>

</style>