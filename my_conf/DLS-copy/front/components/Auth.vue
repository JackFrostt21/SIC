<template>
  <div style= "background-image: url('img/auth-bg.png')" class="bg-cover bg-center w-screen h-screen">

    <div class="h-[122px]"></div>
    <img src="../public/img/eng-logo.png" class="mx-auto">

    <div class="w-[514px] h-[385px] mt-[21px] rounded-[20px] bg-white shadow-[0px_0px_100px_0px_rgba(0,0,0,0.1)] mx-auto relative">

      <h1 class="absolute top-[30px] left-[31.21px] w-[405.79px] h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black">
        Вход в учебный портал
      </h1>

      <div class="absolute top-[80px] left-[31.21px] w-[460px] h-[83px]">

        <div class="w-[49px] h-[22px] flex items-center">
          <span class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]">Логин</span>
        </div>

        <input
          id="inputLogin"
          type="text"
          class="w-[451px] h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[20px] pb-[17px] pl-[20px] gap-[10px] 
          text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
        />

      </div>

      <div class="absolute top-[169px] left-[31.21px] w-[460px] h-[75px]">

        <div class="w-[49px] h-[22px] flex items-center">
          <span class="font-sans text-[16px] font-normal leading-none tracking-[0%] text-[#8A8A8A]">Пароль</span>
        </div>


        <div class="relative">

          <input
            id="inputPassword"
            :type="visible ? 'text' : 'password'" 
            class="w-[451px] h-[46px] mt-[6px] rounded-[10px] border border-[#E6E6E6] pt-[17px] pr-[45px] pb-[17px] pl-[20px] gap-[10px] 
            text-black bg-[#E6E6E6] focus:outline-none focus:ring-1 focus:ring-[#909090] not-placeholder-shown:bg-white"
           />

          <img v-if="visible" src="../public/img/eye-on.png" @click="toggleHidePassword" class="absolute top-[17px] left-[409.79px] transform"/>
          <img v-else src="../public/img/eye-off.png" @click="toggleHidePassword" class="absolute top-[17px] left-[409.79px] transform"/>

        </div>

       
      </div>

      <div v-if="stat" class="absolute top-[250px] left-[31px] w-[22.89px] h-[22px] rounded-[5px] border border-[#8A8A8A] relative" 
            @click="toggleRememberPassword">

            <img src="../public/img/r-password.svg" class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />

      </div>

      <div v-else class="absolute top-[250px] left-[31px] w-[22.89px] h-[22px] rounded-[5px] border border-[#8A8A8A]" @click="toggleRememberPassword">

          

      </div>

      <h1 class="w-[135.26px] h-[19px] absolute top-[254px] left-[62.43px] font-sans font-normal text-[14px] leading-none text-black">
        Запомнить пароль
      </h1>

      <NuxtLink to="/reset-password" class="absolute top-[254px] left-[327.79px] w-[153.99px] h-[19px] font-sans font-semibold text-[14px] leading-none underline decoration-solid underline-offset-0 decoration-0 text-[#0C1E45]">
        Восстановить пароль
      </NuxtLink>

      <div class="w-[451px] h-[53px] absolute top-[302px] left-[31px] rounded-[10px] px-[80px] py-[17px] bg-[#0C1E45] 
      text-white flex items-center justify-center gap-[10px] transition-colors duration-100 hover:bg-[#3D4B6A] active:bg-[#8A8A8A]">

          <h1 class="w-[51px] h-[22px] font-sans font-semibold text-base leading-none tracking-[0%] text-center">
            Войти
          </h1>

      </div>
                
    </div>
  </div>    
</template>

<script>
export default {
  data() {
    return {
      stat: false, // начальное состояние для (запомнить пароль)
      visible: false //начальное состояние для (скрыть пароль)
    }
  },
  methods: {
    toggleRememberPassword() {
      this.stat = !this.stat; 
    },

    toggleHidePassword() {
      this.visible = !this.visible;
    }
  }
}
</script>

<style>

</style>