<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <UserInfo />
    <UserToolBar class="md:flex hidden"/>

    <div class="w-full flex flex-row gap-0 md:hidden">

      <p class="font-sans font-semibold text-[14px] my-auto ml-[15px]">Обо мне</p>

      <NuxtLink to="/profile/results">

        <img src="/public/img/profile_nextpage.svg" class="w-[25px] h-[29px] mt-[3px]"/>

      </NuxtLink>

    </div>
    <AboutUser />
    
    
  </div>
</template>


<style>
body {
  background: #F2F2F2;
}
</style>