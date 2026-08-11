<template>
  <div class="flex flex-col gap-[10px] h-auto w-full sm:w-[1040px]">

    <div class="sm:w-[1040px] sm:h-[30px]">

      <span class="font-semibold text-[22px] leading-[1] tracking-normal text-black" style="font-family: 'Open Sans', sans-serif;">
        Обязательные курсы
      </span>

    </div>

    <p v-if="no_courses" class="h-[22px] font-semibold text-[16px] leading-[1] tracking-[0] text-[#8A8A8A] font-sans mb-[40px]">В настоящий момент для вас нет доступных обязательных программ обучения.
      Пожалуйста, обратитесь к администратору для получения доступа.</p>

    <div v-else class="flex flex-col md:flex-row md:flex-wrap gap-[6px]">

      <CourseCard3
      v-for="item in items" 
      :key="item.id"
      :name="item.title"
      :is_nessary="item.obligatory"
      :percent="item.min_test_percent_course"
      :url="item.image_course"
      :id_course="item.id"
      :ddl="item.deadline"
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
});

const no_courses = ref(props.items.length === 0)

watch(() => props.items, (newItems) => {
  no_courses.value = newItems.length === 0
  console.log('Обновлены все курсы:', newItems)
}, { immediate: true })

</script>

<style>

</style>