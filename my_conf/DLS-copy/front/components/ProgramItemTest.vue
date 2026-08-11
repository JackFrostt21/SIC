<template>

  <div class="md:w-[1040px] w-full h-[135px] rounded-[10px] bg-white flex flex-row gap-[40px] items-center">

    <div class="w-fit h-[90%] flex items-center ml-[20px]">
      <img 
        :src="props.url" 
        class="max-w-full max-h-full object-contain rounded-[10px]"
      >
    </div>

    <div class="flex flex-col md:gap-[15px] gap-[6px]">

    <div class="md:w-[555.02px]">
      <p class="font-sans font-semibold md:text-[14px] text-[12px] leading-[100%] tracking-[0%] text-[#8A8A8A]">Тест</p>
    </div>

    <div class="md:w-[555.02px] max-w-[70%]">
      <p class="font-open-sans font-semibold md:text-[16px] text-[14px] leading-[100%] tracking-[0%] text-[#000000]">{{ props.name }}</p>
    </div>

    <div class="flex flex-row gap-[10px] items-center">

      <NuxtLink :to="'/study/test/' + props.course_id + '/'">
      <ProgramButtonGo class="" :isComplete="progress"/>
    </NuxtLink>


    <ProgramProgressBar :progress="res" class=""/>


    <div class="md:w-[138px] md:h-[22px] w-[102px] h-[16px] relative items-center">

      <img src="../public/img/alert-circle.svg" class="absolute md:top-[2px] top-[1px]"/>

      <span class="md:block hidden md:w-[115px] w-[85px] h-[22px] inline-flex items-center font-bold md:text-[16px] text-[14px] leading-[1] text-[#D21E41] font-sans absolute left-[23px] top-[1px] md:top-[5px]">
        Обязательно!
      </span>

    </div>


    </div>

    </div>
  </div>
</template>


<script setup>
const props = defineProps({
  course_id: {
    default: 1
  },
  test_id: {
    default: 1
  },
  name: {
    default: 'Тест'
  },
  url: {
    default: ''
  }

})

const tests = useTest();
const test_res = await tests.getTestPerUser(props.test_id);

localStorage.setItem('courseId', props.course_id);


const res = ref()

if (!test_res.test) {

  res.value = 0

} else {

  res.value = test_res.test.quantity_correct
}

console.log(test_res)
</script>



<style>
.image-wrapper {
  aspect-ratio: var(--aspect-ratio);
}
</style>