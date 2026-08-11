<template>
  <div class="flex flex-row md:w-[1040px] w-full h-[160px] md:h-[182px] rounded-[10px] gap-[10px] items-center bg-white">

    <div class="w-fit h-[90%] flex items-center ml-[20px]">
      <img 
        :src="url || '/img/course.svg'" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
    </div>


    <div class="flex flex-col gap-[7px]">

      <div class="font-sans font-semibold md:text-[22px] text-[14px] leading-[100%] tracking-[0%] text-[#000000]">
        {{ name }}
      </div>

      <div class="md:w-[153px] md:h-[19px] font-sans font-semibold text-[14px] leading-[100%] tracking-[0%] text-[#8A8A8A]">
        Программа обучения
      </div>

      <div class="flex md:flex-row gap-[10px] items-center">

        <ProgramButtonGo class="" :isComplete="isDone"/>

        <ProgramProgressBar class="" :progress="percent"/>

        <div class="md:flex flex-row gap-[11px] hidden">

          <ProgramTag v-for="tag in tags" :key="tag" :id="tag"/>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { useStat } from '#imports';

const courseStat = useStat();

const props = defineProps({
  name: {
    type: String,
    default: 'Молния'
  },
  progress: {
    type: Number,
    default: 0
  },
  tags: {
    type: Array,
    default: () => []
  },
  url: {
    type: String,
    default: '../public/img/course.svg' // Исправлена опечатка в courceimg → courseimg
  },
  course_id: {
    default: 1
  }
});

const course = await courseStat.getStatCourse(props.course_id);

console.log(course)

console.log('Аватарка курса: ', props.url)

const percent = course.course.reading_progress_percent;
const isDone = course.course.is_completed

console.log(percent)

console.log('Полученные теги: ', props.tags)
</script>

<style>

</style>