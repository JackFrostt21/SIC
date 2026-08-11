<template>
  <NuxtLink :to="/study/+id_course">
  <div class="w-100 h-[143px] sm:w-[1040px] sm:h-[188px] rounded-[10px] bg-white relative">

    <DeadLine v-if="ddl" :ddl="ddl"/>

    <img :src="url" class="w-[49px] h-[44px] sm:w-[186px] rounded-[10px] sm:h-[165px] absolute top-[8px] left-[16px] object-contain bg-[#E6E6E6]" />

    <p class="absolute top-[19px] left-[84px] sm:top-[23px] sm:left-[216px] font-semibold text-[14px] sm:text-[18px] leading-[100%] tracking-normal text-black" style="font-family: 'Open Sans', sans-serif;">
      {{ name }}
    </p>

    <div v-if="!notCourse" class="top-[65px] left-[16px] sm:w-[182px] sm:h-[19px] font-semibold text-[14px] leading-[1] tracking-[0px] text-black font-sans absolute sm:left-[216px] sm:top-[75px]">
      {{ tems}} из {{ all_tems }} тем пройдено
    </div>
    <div v-else class="h-[19px] font-semibold text-[14px] leading-[1] tracking-[0px] text-black font-sans absolute left-[216px] top-[75px]">
      Курс недоступен, обратитесь к администратору
    </div>

    <ProgressBar :percent=percent class="absolute top-[85px] left-[16px] sm:top-[102px] sm:left-[216px]"/>

    <CourceCardButton v-if="!notCourse" class="absolute top-[97px] left-[16px] sm:top-[120px] sm:left-[216px]" :is-complete="isDone"/>

    <CourseIsNessary v-if="is_nessary" class="absolute top-[130px] left-[422px]"/>
    
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