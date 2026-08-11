<template>
  <div class="flex flex-col w-full gap-[14px] mb-[30px]"> <!-- Убрал фиксированную высоту, добавил margin-bottom -->
  
    <p class="w-full font-semibold text-[14px] leading-[1] text-[#8A8A8A] font-open-sans">
      {{ title }}
    </p>

    <p 
      v-if="no_courses" 
      class="font-semibold md:text-[16px] text-[14px] leading-[1.4] text-[#8A8A8A] font-sans mb-[40px]"
    >
      В настоящий момент для вас нет доступных программ обучения.
      Пожалуйста, обратитесь к администратору для получения доступа.
    </p>

    <div v-else class="flex flex-col md:flex-row md:flex-wrap gap-[6px]"> <!-- Или flex flex-wrap gap-4 -->
      <CourseCard3
        v-for="item in items" 
        :key="item.id"
        :name="item.title"
        :is_nessary="item.obligatory"
        :percent="item.min_test_percent_course"
        :url="item.image_course"
        :id_course="item.id"
      />

    </div>

  </div>
</template>

<script setup>

import { ref, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => [],
  },
  title: {
    default: 'Обязательные к изучению'
  }
});

const no_courses = ref(props.items.length === 0)

console.log('что тут', props.items)

</script>

<style>

</style>