<template>
  <div v-if="isComplete" class="flex flex-row items-center justify-center md:w-[190px] w-[144px] md:h-[40px] h-[32px] rounded-[10px] bg-[#E6E6E6]">

    <span class="md:text-[16px] text-[14px] md:w-[72px] font-semibold leading-none text-[#8A8A8A] font-sans">
      Пройден
    </span>

  </div>
  <div v-else class="flex flex-row items-center justify-center md:w-[190px] w-[144px] md:h-[40px] h-[32px] rounded-[10px] bg-[#0C1E45]">

    <span class="md:text-[16px] text-[14px] md:w-[72px] font-semibold leading-none text-white font-sans">
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

<style>



</style>