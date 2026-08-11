<template>
  <div class="md:w-[1040px] w-[90%] h-[128px] rounded-[10px] bg-white mx-auto relative">

    <span class="md:w-[509.5px] h-[25px] font-semibold md:text-[18px] text-[16px] leading-[1] tracking-[0] text-black top-[20px] left-[20px] font-sans absolute" >
      Аватар
    </span>

    <span class="md:w-[180px] h-[16px] font-[600] text-[12px] leading-[12px] tracking-[0px] font-sans text-[#8A8A8A] absolute md:left-[100px] left-[93px] md:top-[25px] top-[45px]">
      Размер изображения до 2 МБ
    </span>
    
    <img :src="url" class="md:w-[50px] md:h-[50px] w-[54px] h-[54px] rounded-[316px] absolute md:top-[59px] top-[55px] left-[20px] object-cover"/>

    <div @click="triggerFileInput" class="flex flex-row w-[190px] h-[40px] rounded-[10px] bg-[#0C1E45] left-[92px] top-[64px] absolute">

      <!-- Скрытый input для выбора файла -->
      <input
        ref="fileInput"
        type="file"
        style="display: none"
        @change="handleFileChange"
      >

      <span class="w-[82px] h-[22px] font-semibold text-[16px] leading-[1] text-white font-sans mt-[10px] ml-[56px]">
        Загрузить
      </span>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAvatar } from '~/composables/useNewAvatar';
import { useStorage } from '@vueuse/core';
import { useUserStore } from '#imports';

const store = useUserStore()
const url = store.image;

const avaStore = useAvatar();

const fileInput = ref(null); // Declare the ref for the input element

const emit = defineEmits(['file-selected']); // Define the custom event


const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click(); // Access the ref's value directly
  }
};

const handleFileChange = async (event) => {
  const file = event.target.files[0];

  if (file) {
    console.log('Выбранный файл: ', file.name);
    emit('file-selected', file); // Emit the event without 'this'

    const feedback = await avaStore.setAva(file);

    console.log(feedback)
  }
};
</script>

<style>
</style>