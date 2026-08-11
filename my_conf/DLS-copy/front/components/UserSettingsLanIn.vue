<template>
  <div class="md:w-[515px] w-full h-auto rounded-[10px] bg-white relative">

    <span class="w-[509.5px] h-[25px] font-semibold text-[18px] leading-[1] tracking-[0] text-black top-[20px] left-[20px] font-sans absolute" >
      Язык интерфейса
    </span>

    <div @click="open = !open" v-if="!open" class="flex w-[232px] h-[40px] rounded-[10px] bg-[#E6E6E6] absolute left-[20px] top-[59px] mb-[17px]">
  
      <span class="w-[71px] h-[22px] font-semibold text-[16px] leading-[1] text-[#8A8A8A] font-sans absolute top-[9px] left-[16px]">
        Выбрать
      </span>

      <img src="../public/img/vector.svg" class="w-[11px] h-[6px] absolute top-[17px] left-[204px]"/>

    </div>

    <div
      v-if="open"
      class="flex flex-row w-[232px] h-[134px] rounded-[10px] pt-[9px] pb-[9px] pr-[80px] pl-[16px] gap-[10px] bg-[#E6E6E6] absolute left-[20px] top-[59px] mb-[17px]"
    >

      <span class="w-[71px] h-[22px] font-semibold text-[16px] leading-[1] text-[#8A8A8A] font-sans absolute top-[9px] left-[16px]">
        Выбрать
      </span>

      <img src="../public/img/vector_up.svg" class="w-[11px] h-[6px] absolute top-[17px] left-[204px]"/>

      <span @click="open = false" class="w-[129.44px] h-[22px] font-semibold text-[16px] leading-[100%] tracking-[0px] text-black font-open-sans absolute top-[41px]">
        Русский
      </span>

      <div class="w-[199px] h-[1px] bg-[#8A8A8A] absolute top-[68px]"></div>

      <span @click="open = false" class="w-[129.44px] h-[22px] font-semibold text-[16px] leading-[100%] tracking-[0px] text-black font-open-sans absolute top-[75px]">
        Английский
      </span>

      <div class="w-[199px] h-[1px] bg-[#8A8A8A] absolute top-[101px]"></div>

      <span @click="open = false" class="w-[129.44px] h-[22px] font-semibold text-[16px] leading-[100%] tracking-[0px] text-black font-open-sans absolute top-[107px]">
        Узбекский
      </span>

  </div>
      
    <div v-if="open" class="fixed inset-0 z-0" @click="open = false"></div>
    
    
  </div>
</template>

<script setup>
import { ref } from "vue";

const languages = ["Русский", "English", "Deutsch"];
const selectedLang = ref(languages[0]);
const open = ref(false);

function selectLang(lang) {
  selectedLang.value = lang;
  open.value = false;
}

</script>

<style>

</style>