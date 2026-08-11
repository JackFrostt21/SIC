<template>
  <div style= "background-image: url('/img/auth-bg.png')" class="bg-cover bg-center w-screen h-screen">

    <div class="h-[122px]"></div>
    <img src="../../public/img/eng-logo.png" class="mx-auto">

    <div class="w-[90%] h-[109px] sm:w-[514px] sm:h-[157px] mt-[21px] rounded-[20px] bg-white shadow-[0px_0px_100px_0px_rgba(0,0,0,0.1)] mx-auto relative">

      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 relative h-full w-[81%] sm:w-full">

      <h1 class="absolute top-[16px] sm:top-[30px] sm:left-[31.21px] sm:w-[405.79px] h-[30px] font-sans text-[22px] font-semibold leading-none tracking-normal text-black">
        Ваш пароль обновлен
      </h1>


      <NuxtLink to="/" class="w-[100%] h-[32px] top-[58px] sm:w-[451px] sm:h-[53px] absolute sm:top-[74px] sm:left-[31px] rounded-[10px] px-[80px] py-[17px] bg-[#0C1E45] 
      text-white flex items-center justify-center gap-[10px] transition-colors duration-100 hover:bg-[#3D4B6A] active:bg-[#8A8A8A]">

          <h1 class="w-[51px] h-[22px] font-sans font-semibold text-base leading-none tracking-[0%] text-center">
            Готово
          </h1>

        </NuxtLink>
      </div>         
    </div>
  </div>    
</template>

<script>
export default {
  data() {
    return {
      contact: 'ivanov.ivan@ivan.com'
    }
  },
  methods: {
  }
}
</script>

<style>

</style>