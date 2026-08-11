<template>
  <div
    style="background-image: url('img/auth-bg.png')"
    class="bg-cover bg-center w-screen h-screen flex flex-col"
  >
    <div class="h-[122px]"></div>
    <img src="../public/img/eng-logo.png" class="mx-auto" />

    <AuthForm />
    <Alert message="Данные для входа можно посмотреть в телеграм боте СДО" duration="1000000" />
  </div>
</template>

<script setup>
  import { createPinia } from 'pinia'
  const pinia = createPinia()
</script>

<style></style>