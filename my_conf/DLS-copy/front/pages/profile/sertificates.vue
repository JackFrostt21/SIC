<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <UserInfo />
    <UserToolBar class="md:flex hidden"/>

    <div class="w-full flex flex-row gap-0 md:hidden">

      <NuxtLink to="/profile/results">

        <img src="/public/img/profile_previospage.svg" class="w-[25px] h-[29px] mt-[3px]"/>

      </NuxtLink>

      <p class="font-sans font-semibold text-[14px] my-auto">Сертификаты</p>

      <NuxtLink to="/profile/settings">

        <img src="/public/img/profile_nextpage.svg" class="w-[25px] h-[29px] mt-[3px]"/>

      </NuxtLink>

    </div>

    <UserSertificates />
    <Alert :message="msg" class="z-1500 hidden md:block"/> 
    
    
  </div>
</template>

<script lang="ts" setup>

const msg = 'Эта страница находится в разработке. Спасибо за понимание!'

</script>

<style>
body {
  background: #F2F2F2;
}
</style>