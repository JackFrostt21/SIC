<template>
  
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <Search />

    <div class="h-auto md:w-[1040px] w-full mx-auto flex flex-col gap-[30px]">

      <span class="font-semibold text-[22px] leading-[1] tracking-normal text-black" style="font-family: 'Open Sans', sans-serif;">
        Рейтинг
      </span>

      <TopThree />
      <TopUser />
      <TopAllUsers />
      
    </div>
    
    <Alert :message="msg" class="z-1500 md:block hidden"/>
  </div>

</template>

<script lang="ts" setup>

const msg = 'Эта страница находится в разработке. Спасибо за понимание!'

</script>

<style>

</style>