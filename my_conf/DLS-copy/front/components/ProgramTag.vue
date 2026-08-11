<template>
  <div class="inline-flex items-center justify-center gap-[3px] rounded-[22px] border-2 border-[#00DCC8] py-[4px] px-[15px]">
    <span class="font-sans font-semibold md:text-[16px] text-[12px] leading-none tracking-normal text-black">
      {{ name.tag }}
    </span>
  </div>
</template>

<script setup>
import { useTag } from '#imports';

const getName = useTag();

const props = defineProps({
  id: {
    type: Number
  }
});

console.log('Полученный id', props.id)

const name = await getName.getTag(props.id)


</script>

<style>

</style>