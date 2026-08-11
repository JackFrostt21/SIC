<template>
  <div class="h-fit w-fit flex flex-row gap-[8px] cursor-pointer" @click="$emit('click')">
    <ProgramTestRound class="my-auto" :isAnsw="!isSelected"/>
    <div class="inline-block md:max-w-[93%] max-w-[85%] text-black font-normal md:text-[16px] text-[14px] leading-[normal] tracking-[0px]">
      {{ answ }}
    </div>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  answ: {
    type: String,
    default: ''
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>