<template>
  
  <div v-if="isVisible" class="absolute top-[10px] left-0 right-0 mx-auto relative w-[1040px] h-[271px]">
  <div v-if="isVisible" class="shadow-md fixed absolute top-0 right-0 w-[253px] h-[271px] rounded-[10px] bg-white z-50">

    <img @click="closePopup" :src="url" class="w-[50px] h-[49.61px] top-[19px] left-[20px] rounded-[316px] absolute object-cover"/>

    <div class="mt-[24px] ml-[83px] w-[134px]">
      <p class="font-sans text-base font-semibold leading-none tracking-normal text-black">
        {{username}}
      </p>
    </div>

    <div class="ml-[83px]">
      <span class="w-[119px] h-[19px] font-sans text-sm font-semibold leading-none tracking-normal text-[#8A8A8A]">
        {{email}}
      </span>
    </div>

    <div class="absolute top-[79px] left-[20px] flex items-center border border-[#00DCC8] rounded-[20px] h-[27.26px] w-fit border-2 px-4 py-1 gap-[10px]">
      <img src="/img/i-award.svg" class="h-[20px]" />
      <p class="text-[14.51px] font-semibold font-sans leading-none">{{ place }}</p>
    </div>

    <div class="absolute left-[142px] top-[79px] flex items-center w-[92.21px] h-[27.26px] px-[13.6px] py-[3.63px] gap-[9.07px] rounded-[19.95px] border border-[#00DCC8] border-[1.81px]">
      <p class="text-[14.51px] font-semibold font-sans leading-none">5 баллов</p>
    </div>

    <NuxtLink to="/profile">
    <div class="absolute top-[52px] left-[20px] w-[110px] h-[20px] relative">
      <img class="absolute top-[3px] left-[0px]" src="../public/img/user-btn.svg"/>
      <div class="absolute top-[2px] left-[15px] w-[85px] h-[20px] text-black flex items-center justify-center font-semibold font-sans text-[14.51px] leading-[100%] tracking-[0px]">Профиль</div>
    </div>
    </NuxtLink>

    <NuxtLink to="/profile/settings">
    <div class="absolute top-[60px] left-[20px] w-[110px] h-[20px] relative">
      <img class="absolute top-[3px] left-[0px]" src="../public/img/settings.svg"/>
      <div class="absolute top-[2px] left-[20px] w-[85px] h-[20px] text-black flex items-center justify-center font-semibold font-sans text-[14.51px] leading-[100%] tracking-[0px]">Настройки</div>
    </div>
    </NuxtLink>

    <div class="absolute top-[68px] left-[20px] w-[110px] h-[20px] relative">
      <img class="absolute top-[3px] left-[0px]" src="../public/img/help-circle.svg"/>
      <div class="absolute top-[2px] left-[22px] w-[85px] h-[20px] text-black flex items-center justify-center font-semibold font-sans text-[14.51px] leading-[100%] tracking-[0px]">Поддержка</div>
    </div>

    <div className="absolute top-[226px] left-[20px] w-[209px] border border-[#E6E6E6]"></div>

    <NuxtLink to="/">
    <div class="absolute top-[110px] left-[20px] w-[110px] h-[20px] relative">
      <img class="absolute top-[3px] left-[0px]" src="../public/img/chevron-left.svg"/>
      <div class="absolute top-[2px] left-[2px] w-[85px] h-[20px] text-black flex items-center justify-center font-semibold font-sans text-[14.51px] leading-[100%] tracking-[0px]">Выйти</div>
    </div>
    </NuxtLink>

  </div>
</div>
</template>

<script>
import { defineProps, defineEmits } from 'vue';

import { useAuthStore } from '@/stores/auth';

const emit = defineEmits(['close']);

export default {
  props: {
    isVisible: {
      type: Boolean,
      required: true
    }
  },

  methods: {
    closePopup() {
      this.$emit('close');
    }
  },

  computed: {
    username() {
      return useAuthStore().user?.username;
    },
    email() {
      return useAuthStore().user?.email;
    },
    url() {
      return useUserStore().image
    }
  },

  data() {

    return{
      place: '2' + ' ' + 'место',
      score: '' + ' ' + 'баллов'
    }
    
  },


  }


</script>

<style>

</style>
