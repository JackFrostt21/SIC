<template>
  <div class="md:w-[1040px] w-full h-[63px] md:h-[69px] rounded-[10px] bg-[#FFFFFF] relative flex flex-row items-center">

    <div class="flex items-center absolute left-[20px]">

    <img v-if="firstPlace" src="../public/img/award1.svg" class="h-[23px] w-[23px] md:w-[26px] md:h-[26px]" />
    <img v-if="secondPlace" src="../public/img/award2.svg" class="h-[23px] w-[23px] md:w-[26px] md:h-[26px]" />
    <img v-if="thirdPlace" src="../public/img/award3.svg" class="h-[23px] w-[23px] md:w-[26px] md:h-[26px]" />

    <p class="font-sans font-semibold md:text-[18px] text-[14px] leading-[100%] tracking-[0em] text-black" v-if="another">139</p>

    <img :src="image" class="ml-[14px] w-[31px] h-[29px] rounded-[5px] object-fill"/>

    <p class="ml-[14px] font-sans font-semibold md:text-[18px] text-[14px] leading-[100%] tracking-[0em]"> {{ username }} </p>

    </div>

    <div class="flex items-center absolute right-[20px]">
      <img src="../public/img/Star.svg" class="md:w-[25px] md:h-[25px] w-[23px] h-[23px] mr-[6px]" />
      <p class="font-sans font-semibold md:text-[18px] text-[14px] leading-[100%] tracking-[0em] text-black">
        {{ place }}
      </p>
    </div>
    
  </div>
</template>

<script>
export default{
  props: {
    firstPlace: {
      type: Boolean,
      default: false
    },
    secondPlace: {
      type: Boolean,
      default: false
    },
    thirdPlace: {
      type: Boolean,
      default: false
    },
    another: {
      type: Boolean,
      default: false
    },
    image: {
      default: '/img/template-usr.png'
    },
    username: {
      default: 'Тест Тестовый Тестович'
    },
    place: {
      default: 139
    }
  }
}

</script>

<style>

</style>