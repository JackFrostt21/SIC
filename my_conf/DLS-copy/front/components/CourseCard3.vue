<template>
  <NuxtLink :to="/study/+id_course">
  <div class="w-full max-w-[340px] h-[300px] sm:w-[340px] sm:h-[360px] rounded-[10px] bg-white flex flex-col gap-[20px] relative items-center">

    <DeadLine v-if="ddl" :ddl="ddl"/>

     <img :src="url || '/img/course.svg'" class="w-full h-[144px] rounded-[10px] sm:w-full rounded-t-[10px] shadow-lg sm:h-[165px] object-fill bg-[#E6E6E6]" />

    <div class="w-[90%] flex flex-col gap-[12px]">


    <p class="font-semibold text-[14px] sm:text-[18px] leading-[100%] tracking-normal text-black" style="font-family: 'Open Sans', sans-serif;">
      {{ name }}
    </p>

    <div v-if="!notCourse" class=" sm:w-[182px] sm:h-[19px] font-semibold text-[14px] leading-[1] tracking-[0px] text-black font-sans">
      {{ tems}} из {{ all_tems }} тем пройдено
    </div>
    <div v-else class="h-[19px] font-semibold text-[14px] leading-[1] tracking-[0px] text-black font-sans">
      Курс недоступен, обратитесь к администратору
    </div>

    <ProgressBar :percent=percent class=""/>

    </div>
    
    <div class="absolute left-[5%] bottom-[3%] flex flex-row gap-[20px] items-center">
      <CourceCardButton v-if="!notCourse" class="" :is-complete="isDone"/>

      <CourseIsNessary v-if="is_nessary" class=""/>
    </div>
    
    
  </div>
</NuxtLink>
</template>

<script setup>
import { useStat } from '#imports';

const courseStat = useStat()

const props = defineProps({
  url: {
    default: "../public/img/img_card.png"
  },
  name: {
    default: 'Обучение технике безопасности для буровых мастеров'
  },
  is_nessary: {
    default: false
  },
  id_course: {
    default: 0
  },
  ddl: {
    default: null
  }
})

const tems = ref('')
const all_tems = ref('')

const notCourse = ref(false)

console.log(props.id_course)

const course = await courseStat.getStatCourse(props.id_course);

console.log(course)

const percent = ref(0)
const isDone = ref(false)

console.log('feed', course)

if (course.course) {

  percent.value = course.course.reading_progress_percent
  isDone.value = course.course.is_completed
  console.log('Выполнен на фронте: ', isDone.value)
  console.log('Выполнено на сервере', course.course.is_completed)
  tems.value = course.course.read_topics;
  all_tems.value = course.course.total_topics;

} else {
  notCourse.value = true
  percent.value = 0
  isDone.value = false
  tems.value = []
  all_tems.value = []
}



</script>

<style>

</style>