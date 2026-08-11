<template>
  <div class="w-full h-[35px] sm:w-[1039.97px] sm:h-[40.01px] mx-auto relative">

  <div class="absolute h-[35px] w-[82%] sm:w-[845px] sm:h-[40.01px] bg-white shadow-md rounded-[10px] relative">

    <input 
      v-model="searchValue"
      @input="handleInput"
      class="sm:h-[40.01px] sm:w-[745px] h-[35px] w-[100%] bg-white rounded-[10px] focus:outline-none focus:ring-0 placeholder-[#8A8A8A] text-sm font-sans text-gray-900 pl-[22px]" 
      placeholder="Поиск курса, программы обучения..."/>

    <div class="md:block hidden w-[20px] h-[20px] top-[11px] right-[13.5px] absolute">
      <img src="../public/img/search.png" class="w-[20px] h-[20px]" />
    </div>

  </div>

  <div class="absolute left-[875px] w-[164.97px] h-[40.01px] rounded-[10px] top-[0px] bg-[#E6E6E6] shadow-md md:block hidden">
      <img src="../public/img/filters.png" class="absolute left-[24px] top-[11.81px] h-[16px] w-[18px]"/>
      <p class="font-sans font-semibold text-[12px] leading-[12px] text-[#8A8A8A] absolute left-[51px] top-[13px]">По умолчанию</p>
  </div>

  <img src="../public/img/filters.png" class="absolute left-[89%] top-[10px] h-[16px] w-[18px] block md:hidden"/>

  <!--Filters v-if="open" class="z-[900]"/-->

  
</div>
</template>

<script setup>
import { ref } from "vue";

const languages = ["Русский", "English", "Deutsch"];
const selectedLang = ref(languages[0]);
const open = ref(false);
const searchValue = ref('');

// Эмиты
const emit = defineEmits(['search']);

// Обработчик ввода
const handleInput = () => {
  emit('search', searchValue.value);
}
</script>

<style>
</style>