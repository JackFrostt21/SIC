<template>
  
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <Search />

    <p class="w-full font-sans text-[18px] font-semibold md:hidden">Новости</p>

    <div class="h-auto flex flex-col gap-1 w-full items-center md:hidden">
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>
      <NewsItem proirity="true" isRead="true"/>

    </div>

    <div class="h-auto w-[1040px] mx-auto flex flex-row gap-[10px] hidden md:flex">

      <NewsToolBar />
      <NewsView />
      
    </div>
    
  <Alert :message="msg" class="z-1500 hidden md:block"/> 
  </div>

</template>

<script lang="ts" setup>

const msg = 'Эта страница находится в разработке. Спасибо за понимание!'

</script>

<style>

</style>