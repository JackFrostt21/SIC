<template>
  <div class="w-[89px] h-[19px] relative">
  
    <div class="absolute top-[3px] w-[37px] h-[19px]">
      <p class="w-full font-sans font-semibold text-[14px] leading-none tracking-normal text-[#8A8A8A]">
        {{ progress }}%
      </p>
    </div>
  
    <div class="absolute top-[10px] left-[35px] w-[39px] h-[4px] rounded-[4px] md:left-[50px] bg-[#E6E6E6] text-center">
    </div>
  
    <div 
      class="absolute top-[10px] left-[35px] h-[4px] rounded-[4px] md:left-[50px] bg-[#00DCC8] text-center z-200"
      :style="{ width: `${progress * 0.39}px` }"
    >
    </div>
  
  </div>
  </template>
  
  <script setup>
  const props = defineProps({
    progress: {
      type: Number,
      required: true,
      default: 0
    }
  });
  </script>
  
  <style>
  
  </style>