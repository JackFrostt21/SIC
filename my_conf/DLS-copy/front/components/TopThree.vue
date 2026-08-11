<template>
  <div class="flex flex-col md:w-[1040px] w-full h-auto gap-[14px]">
  
    <p class="md:w-[1040px] md:h-[19px] font-semibold text-[14px] leading-[1] text-[#8A8A8A] font-open-sans">
      ТОП 3
    </p>


    <PlaceItem firstPlace="true" />
    <PlaceItem secondPlace="true" />
    <PlaceItem thirdPlace="true" />
    

  </div>
</template>

<script>

export default{
  props: {
    title: {
      default: 'Обязательные к изучению'
    }
  }
}

</script>

<style>

</style>