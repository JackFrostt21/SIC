<template>
  
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <Search />

    <div class="h-auto md:w-[1040px] w-[90%] mx-auto flex flex-col gap-[30px]">

      <span class="font-semibold text-[22px] leading-[1] tracking-normal text-black" style="font-family: 'Open Sans', sans-serif;">
        Обучение
      </span>

      <StudyItem  :items="courses.nessary"/>

      <StudyItem v-for="tema in tems.tems" :key="tema.id" :title="tema.title" :items="tema.courses" class="mb-[30px]"/>
    </div>
    
    
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCourses } from '#imports'
import { useTems } from '#imports'

// Порядок инициализации:
const userCourse = useCourses()
const userTems = useTems()

// Асинхронная функция должна быть объявлена до хуков
const getCourse = async () => {
  const feedback = await userCourse.getCourses()
  return ({all: feedback.all, nessary: feedback.nessary})
}

const courses = await getCourse();

const tems = await userTems.getTems();

console.log('debug', tems)

console.log(tems, courses);

</script>

<style>

</style>