<template>
  <div 
    class="w-[25.75px] h-[25.75px] border border-[1.84px] rounded-full cursor-pointer"
    :class="isAnsw ? 'border-[#8A8A8A]' : 'bg-[#0C1E45]'"
    @click="$emit('click')"
  ></div>
</template>

<script lang="ts" setup>
defineProps({
  isAnsw: {
    type: Boolean,
    default: true
  }
})

defineEmits(['click'])
</script>