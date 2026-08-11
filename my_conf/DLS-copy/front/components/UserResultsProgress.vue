<template>
  <div class="w-[90%] md:w-[1040px] h-[174px] rounded-[10px] bg-white mx-auto relative">

    <span class="md:w-[509.5px] h-[25px] font-semibold md:text-[18px] text-[16px] leading-[1] tracking-[0] text-black top-[20px] left-[20px] font-sans absolute" >
      Обучение
    </span>

    <span class="md:w-[509.5px] h-[22px] font-semibold md:text-[16px] text-[14px] leading-[1] tracking-[0] text-[#8A8A8A] font-sans absolute left-[20px] top-[61px]">
      Прогресс
    </span>

    <span class="md:w-[509.5px] h-[33px] font-bold md:text-[24px] text-[20px] leading-[1] tracking-[0] text-black font-sans absolute left-[20px] top-[90px]">
      {{progress}}%
    </span>
    
    <ProgressBar class="absolute left-[20px] top-[125px] z-10" :percent="progress"/>

    <span class=" h-[19px] text-[14px] leading-[1] font-semibold font-sans text-black absolute left-[20px] top-[140px]">
      Доступно {{ feedback.stat.summary.total_courses + feedback.stat.summary.total_topics + feedback.stat.summary.total_tests }}
    </span>

    <span class=" h-[19px] text-[14px] leading-[1] font-semibold font-sans text-black absolute left-[121px] top-[140px]">
      Пройдено {{ feedback.stat.summary.completed_courses + feedback.stat.summary.read_topics + feedback.stat.summary.passed_tests }}
    </span>

    <span class=" h-[19px] text-[14px] leading-[1] font-semibold font-sans text-black absolute left-[227px] top-[140px]">
      Не сдано {{ feedback.stat.summary.failed_tests }}
    </span>

  </div>
</template>

<script setup>
import { useStat } from '#imports';
import ProgressBar from './ProgressBar.vue';

const stat = useStat();

const feedback = await stat.getStat();

console.log(feedback);

const progress = feedback.stat.summary.overall_progress;
console.log(feedback.stat.summary.overall_progress)
console.log(progress);

</script>

<style>

</style>