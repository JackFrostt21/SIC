<template>
  <div v-if="fire" class="w-[94px] h-[28px] rounded-tl-[10px] rounded-br-[10px] bg-[#D21E41] absolute top-[0px] relative z-10">
    
    <img src="../public/img/clock.svg" class="w-[16px] h-[16px] left-[8px] top-[6px] absolute" />

    <div class="w-[56px] h-[19px] flex items-center justify-center absolute top-[5px] left-[29px]">
      <span class="text-white font-semibold text-[14px] leading-[14px] font-sans">{{ ddl }}</span>
    </div>

  </div>
  <div v-else class="w-[94px] h-[28px] rounded-tl-[10px] rounded-br-[10px] bg-[#E6E6E6] absolute top-[0px] relative z-10">
    
    <img src="../public/img/clock-gray.svg" class="w-[16px] h-[16px] left-[8px] top-[6px] absolute" />

    <div class="w-[56px] h-[19px] flex items-center justify-center absolute top-[5px] left-[29px]">
      <span class="text-black font-semibold text-[14px] leading-[14px] font-sans">{{ ddl }}</span>
    </div>

  </div>
</template>


<script>

export default{
  props: {
    ddl: {
      default: '16.04.25'
    },
    fire: {
      default: false
    }
  }
}

</script>

<style>

</style>