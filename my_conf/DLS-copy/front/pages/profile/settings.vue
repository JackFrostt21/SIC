<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header class="z-100"/>
    <UserInfo />
    <UserToolBar class="md:flex hidden"/>

    <div class="w-full flex flex-row gap-0 md:hidden">

      <NuxtLink to="/profile/sertificates">

        <img src="/public/img/profile_previospage.svg" class="w-[25px] h-[29px] mt-[3px]"/>

      </NuxtLink>

      <p class="font-sans font-semibold text-[14px] my-auto">Настройки</p>

    </div>

    <UserSettingsAvatar />

    <div class="flex md:flex-row flex-col absolute md:w-[1041px] w-[90%] md:h-[116px] relative gap-[11px]">

      <UserSettingsPassword />
      <UserSettingsLogin />

    </div>

    <div class="flex md:flex-row flex-col md:w-[1041px] w-[90%] md:h-[116px] gap-[11px]">

      <UserSettingsLanIn />
      <UserSettingsLanContent />

    </div>
    
    
  </div>
</template>

<script lang="ts" setup>

</script>

<style>
body {
  background: #F2F2F2;
}
</style>