<template>
  <div class="w-full bg-gray-200 rounded-[4px] h-[4px]">
    <div 
      class="h-full rounded-[4px] bg-[#00DCC8]" 
      :style="{ width: percent + '%' }">
    </div>
  </div>
</template>

<script>
export default {
  props: {
    percent: {
      type: Number,
      default: 20
    }
  }
}
</script>

<style>

</style>