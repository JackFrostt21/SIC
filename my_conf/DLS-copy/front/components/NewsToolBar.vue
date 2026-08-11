<template>
  <div class="w-[340px] h-[533px] rounded-[10px] bg-[#FFFFFF] relative">

    <p class="font-sans font-semibold text-[22px] leading-[100%] tracking-[0em] text-black absolute top-[20px] left-[20px] mb-[20px]">
      Новости
    </p>

    <div class="h-[449px] w-full overflow-auto absolute top-[64px]" style="overflow-x: hidden;">


      <NewsItem proirity="true" isRead="true"/>
      <NewsItem />
      <NewsItem isRead="true"/>
      <NewsItem proirity="true"/>
      <NewsItem />
      <NewsItem isRead="true"/>

    </div>
    
  </div>
</template>

<script>

</script>

<style>


</style>