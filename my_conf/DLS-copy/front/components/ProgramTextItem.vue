<template>

  <div class="md:w-auto w-full h-auto left-0 right-0 mx-auto absolute relative">

    <div class="h-[28px] md:w-[689px] w-full left-0 right-0 mx-auto absolute relative">

      <div class="flex abolute top-[0px] left-[0px] items-center justify-center w-[28px] h-[28px] border-2 border-[#8A8A8A] rounded-full">
        <img src="../public/img/texticon.svg" />
      </div>

      <div class="md:w-[554.74px] max-w-[90%] md:h-[22px] absolute pr-[20px] top-[5px] left-[40px]">
        <p class="font-sans font-semibold text-[14px] leading-none tracking-normal text-black">
          {{ title }}
        </p>
      </div>

    </div>

    <div class="md:w-[689px] w-full h-auto rounded-[10px] mt-[14px] bg-white absolute left-0 right-0 mx-auto">

      <div v-html="desc" class="pd:w-[644px] pt-[20px] pl-[20px] pr-[20px] pb-[95px] font-sans font-semibold md:text-[16px] text-[14px] leading-[136%] tracking-[0%] text-[#000000]">
      </div>
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
 desc: {
  default: 'Ничего не найдено'
 },
 title: {
  default: 'Неизвестный'
 }
})


</script>

