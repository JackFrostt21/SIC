<template>
  <div v-if="!showMobileMenu" class="shadow bg-white w-full">
  <div class="md:w-[1280px] md:h-[70px] w-full h-[42px] mx-auto items-center relative">
    <img src="/img/eng-logo.png" class="absolute md:top-[19px] md:left-[120px] top-[8%] left-[5%]"/>

    <div class="absolute top-[30px] left-[533px] w-[412px] h-[16px] relative md:block hidden">

      <NuxtLink to="/sdo/" class="absolute w-[67px] h-[16px] text-[#8A8A8A] font-sans font-semibold text-base leading-none tracking-[0%] active:text-black">
        Главная
      </NuxtLink>

      <NuxtLink to="/study/" class="absolute w-[81px] h-[16px] left-[101px] text-[#8A8A8A] font-sans font-semibold text-base leading-none tracking-[0%] active:text-black">
        Обучение
      </NuxtLink>

      <NuxtLink to="/news/" class="absolute w-[69px] h-[16px] left-[216px] text-[#8A8A8A] font-sans font-semibold text-base leading-none tracking-[0%] active:text-black">
        Новости
      </Nuxtlink>

      <NuxtLink to="/top/" class="absolute w-[67px] h-[16px] left-[319px] text-[#8A8A8A] font-sans font-semibold text-base leading-none tracking-[0%] active:text-black">
        Рейтинг
      </Nuxtlink>

    </div>
    
    <img src="../public/img/notification.png" class="absolute md:left-[952px] md:top-[26px] left-[82%] top-[26%]"/>

    <div  ref="profileButton" @click="showPopup = !showPopup" class="md:block hidden w-[165px] h-[38px] absolute top-[4px] left-[995px] rounded-[10px] border border-[#F2F2F2] py-[7px] px-[40px] bg-[#F2F2F2] gap-[8px] relative overflow-hidden">

      <div class="mx-auto h-[24px] relative flex items-center justify-center">

        <div class="flex items-center" @click="openModal" @close="closeModal">

          <img src="../public/img/user-icon.svg" class="h-[24px] w-[24px]" alt="User Icon"/>

          <span class="ml-[8px] font-sans text-base font-semibold text-black leading-none tracking-normal">

            {{ username }}

          </span>


        </div> 

      </div>

    </div>


    <ProfilePopup :isVisible="showPopup" @close="showPopup = false"  />

    <img @click="showMobileMenu = !showMobileMenu" src="/public/img/menu.svg" class="md:hidden block h-[12px] w-[14px] absolute top-[38%] left-[91%]" alt="menu" />

  </div>
</div>
<div v-else class="shadow relative bg-white w-full h-[209px] rounded-b-[10px]">

  <div class="md:w-[1280px] md:h-[70px] w-full h-[42px] mx-auto items-center relative">
    <img src="/img/eng-logo.png" class="absolute md:top-[19px] md:left-[120px] top-[8%] left-[5%]"/>
    <img src="../public/img/notification.png" class="absolute md:left-[952px] md:top-[26px] left-[82%] top-[26%]"/>
    <img @click="showMobileMenu = !showMobileMenu" src="/public/img/menu.svg" class="md:hidden block h-[12px] w-[14px] absolute top-[38%] left-[91%]" alt="menu" />
  </div>

  <div class="h-[167px] w-full absolute top-[42px] flex flex-col p-[8px]">

    <NuxtLink to="/profile" class="flex flex-row gap-[6px] items-center ml-[16px]">
      <img class="h-[17px] w-[17px]" src="/public/img/profile.svg" />
      <p class="font-sans font-semibold text-sm leading-loose tracking-normal">Профиль</p>
    </NuxtLink>

    <div class="h-[1px] w-full bg-[#DCDCDC]"></div>

    <NuxtLink to="/sdo/" class="flex flex-row gap-[6px] items-center ml-[16px]">
      <img class="h-[17px] w-[17px]" src="/public/img/main.svg" />
      <p class="font-sans font-semibold text-sm leading-loose tracking-normal">Главная</p>
    </NuxtLink>

    <div class="h-[1px] w-full bg-[#DCDCDC]"></div>

    <NuxtLink to="/study/" class="flex flex-row gap-[6px] items-center ml-[16px]">
      <img class="h-[17px] w-[17px]" src="/public/img/study.svg" />
      <p class="font-sans font-semibold text-sm leading-loose tracking-normal">Обучение</p>
    </NuxtLink>

    <div class="h-[1px] w-full bg-[#DCDCDC]"></div>

    <NuxtLink to="/news/" class="flex flex-row gap-[6px] items-center ml-[16px]">
      <img class="h-[17px] w-[17px]" src="/public/img/news.svg" />
      <p class="font-sans font-semibold text-sm leading-loose tracking-normal">Новости</p>
    </NuxtLink>

    <div class="h-[1px] w-full bg-[#DCDCDC]"></div>

    <NuxtLink to="/top/" class="flex flex-row gap-[6px] items-center ml-[16px]">
      <img class="h-[17px] w-[17px]" src="/public/img/top.svg" />
      <p class="font-sans font-semibold text-sm leading-loose tracking-normal">Рейтинг</p>
    </NuxtLink>

  </div>

</div>
</template>

<script>

import { ref } from 'vue';
import ProfilePopup from './ProfilePopup.vue';
import { useAuthStore } from '@/stores/auth';

export default {

  components: {
    ProfilePopup
  },

  data() {
    const authStore = useAuthStore();
    const username = authStore.user?.username;
    return {
      username: username,
      showPopup: false,
      profileButton: null,
      showMobileMenu: false
    }
  },
  methods: {
  }
}

  
</script>

<style>
</style>