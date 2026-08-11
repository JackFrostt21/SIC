<template>
  <div class="md:w-[1040px] w-full h-auto mx-auto">
  <div class="flex flex-row gap-[30px] w-[494px] h-[22px]">

    <NuxtLink to="/profile" :class="{'active': isActive('/profile')}" class="tab-link" style="width: 69px; height: 22px;">Обо мне</NuxtLink>
    <NuxtLink to="/profile/results" :class="{'active': isActive('/profile/results')}" class="tab-link" style="width: 134px; height: 22px;">Мои результаты</NuxtLink>
    <NuxtLink to="/profile/sertificates" :class="{'active': isActive('/profile/sertificates')}" class="tab-link" style="width: 112px; height: 22px;">Сертификаты</NuxtLink>
    <NuxtLink to="/profile/settings" :class="{'active': isActive('/profile/settings')}" class="tab-link" style="width: 89px; height: 22px;">Настройки</NuxtLink>

  </div>
  </div>
</template>

<script lang="ts" setup>
import { NuxtLink } from '#components';
import { useRoute } from 'vue-router'
const route = useRoute()
const isActive = (path) => route.path === path
</script>

<style>

.tab-link {
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 100%;      /* или 16px */
  letter-spacing: 0;
  color: #8A8A8A;
}

.tab-link.active {
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 100%;
  letter-spacing: 0;
  color: #000000;
}
</style>