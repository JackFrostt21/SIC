<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-1500"/>
    <Search class="z-100"/>

    <div class="md:w-[1040px] w-full h-[19px] mx-auto relative">

      <NuxtLink to="/sdo/" class="absolute w-[86px] h-[19px] top-[1px] md:right-[0px]">

          <img src="../../../public/img/back.svg" class="absolute top-[1px] left-[0px]"/>
          <span class="font-sans font-semibold md:text-[14px] text-[12px] leading-[100%] tracking-[0%] w-[71px] h-[19px] left-[15px] absolute top-[0px] text-[#8A8A8A]">
            Все курсы
          </span>

      </NuxtLink>

      <!--div class="absolute w-[86px] h-[19px] top-[1px] left-[0px]">

        <img src="../../../public/img/back.svg" class="absolute top-[1px] left-[0px]"/>
        <span class="font-sans font-semibold text-[14px] leading-[100%] tracking-[0%] w-[71px] h-[19px] left-[15px] absolute top-[0px] text-[#8A8A8A]">
          Назад
        </span>

      </div-->

    </div>

    <ProgramTestItem class="absolute mx-auto" :info="test"/>


    
  </div>
</template>

<script setup>
import { useCoursesStore } from '#imports';
import { useTest } from '#imports';
// Получаем параметры маршрута
const route = useRoute();
// Извлекаем ID как строку (параметры маршрута всегда строки)
const id = route.params.id;
console.log('Longread id topic', id);
const getTest = useTest();

const test = await getTest.getTest(id)
const title = test.test.title;


console.log(title)


</script>

<style>

</style>