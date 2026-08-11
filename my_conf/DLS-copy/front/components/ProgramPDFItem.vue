<template>

  <div class="w-[90%] h-auto flex flex-col gap-[15px]">

    <div class="flex flex-row gap-[10px] items-center">

      <img src="../public/img/file.svg" class="w-[31px] h-[30px]]"/>

      <div class="h-[22px]">
        <p class="font-sans font-semibold md:text-base text-[12px] leading-none tracking-normal text-black">
          {{ title }}
        </p>
      </div>

    </div>

  <object class="w-full h-[700px]" 
            :data= "props.desc"
            >
    </object>
     
    
    
  </div>
</template>

<script setup>
import { ProgramPDFViewer } from '#components';

const props = defineProps({
 desc: {
  default: 'Ничего не найдено'
 },
 title: {
  default: 'Неизвестный'
 }
})

console.log(props.desc)
</script>

<style>

</style>