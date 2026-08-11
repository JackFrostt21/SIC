<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-1500"/>
    <Search class="z-100"/>

    <div class="absolute md:w-[1040px] w-full h-[215px] mx-auto relative">

      <NuxtLink to="/study" class="absolute w-[86px] h-[19px] top-[1px] left-[1px]">

        <img src="../../public/img/back.svg" class="absolute top-[1px] left-[0px]"/>
        <span class="font-sans font-semibold text-[14px] leading-[100%] tracking-[0%] md:w-[71px] md:h-[19px] left-[15px] absolute top-[0px] text-[#8A8A8A]">
          Все курсы
        </span>

      </NuxtLink>

      <ProgramInfo class="absolute top-[33px]" :name="coursee.title" :url="coursee.image_course" :tags="coursee.tag" :course_id="id"/>
      <div class="flex flex-col gap-[15px] h-auto md:w-[1040px] w-full absolute top-[288px]">
        <div v-if="test_persist" class="flex flex-col gap-[14px] mb-[40px] last:mb-0">
            <!-- Заголовок с иконкой -->
            <div @click="toggleOpen" class="flex items-center cursor-pointer h-[25px]">
              <span class="font-sans font-semibold md:text-[18px] text-[16px] text-black">
                  Итоговый тест
              </span>
              <img 
                v-if="!isOpen" 
                src="../../public/img/vector_up.svg" 
                class="ml-[8px] w-[15px] h-[9px]"
              />
              <img 
                v-else 
                src="../../public/img/vector.svg" 
                class="ml-[8px] w-[15px] h-[9px]"
              />
            </div>

            <!-- Раскрывающийся контент -->
            <div v-if="isOpen" class="flex flex-col gap-[14px] transition-all duration-300">

              <ProgramItemTest :course_id="id" :test_id="test_res.test.id" :name="coursee.title" :url="'/img/test.svg'"/>

            </div>
        </div>





        <ProgramList v-for="program in feedback.topics" :key="program.id" :name="program.title" :info="program" :id_topic="program.id" :course_id="id"/>
      </div>
      



    </div>
  </div>
</template>

<script setup>
import { useCoursesStore } from '#imports';
import { useTopics } from '#imports';
import { useTest } from '#imports';

// Получаем параметры маршрута
const route = useRoute();
// Извлекаем ID как строку (параметры маршрута всегда строки)
const id = route.params.id;

const test_persist = ref(false);


// Сохраняем ID в localStorage
if (process.client) {
  localStorage.setItem('courseId', id.toString());
}

const isOpen = ref(false);

const toggleOpen = () => {
  isOpen.value = !isOpen.value;
};

const coursesStore = useCoursesStore();

const coursee = coursesStore.courses.find(course => course.id === Number(id));

console.log('Тэги: ', coursee.tag)

console.log(id);

console.log('Сам курс: ', coursee.test);

const getTopic = useTopics();


const tests = useTest();
const test_res = await tests.getTest(id);

console.log('Итоговый тест курса: ', test_res);

if (test_res.success) {
  test_persist.value = true
}

const res = ref()

if (!test_res.test) {

  res.value = 0

} else {

  res.value = test_res.test.quantity_correct
}


const feedback = await getTopic.getTopics(id);
console.log('feed', feedback);
</script>

<style>

</style>