<template>
  <div v-if="isComplete" class="flex flex-row items-center justify-center w-[144px] h-[32px] sm:w-[190px] sm:h-[40px] rounded-[10px] bg-[#E6E6E6]">

    <span class="sm:text-[16px] text-[14px] font-semibold leading-none text-black font-sans">
      Пройден
    </span>

  </div>
  <div v-else class="flex flex-row items-center justify-center w-[144px] h-[32px] sm:w-[190px] sm:h-[40px] rounded-[10px] bg-[#0C1E45]">

    <span class="sm:text-[16px] text-[14px] sm:w-[72px] font-semibold leading-none text-white font-sans">
      Пройти
    </span>

  </div>
</template>

<script>
export default{
  props: {
    isComplete: {
      default: false
    }
  }
  
}

</script>