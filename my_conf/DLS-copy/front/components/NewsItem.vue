<template>
  <div class="md:w-[340px] w-[95%] h-[124px] rounded-[10px] bg-white relative" >

    <div class="flex flex-row w-[270px] h-[22px] gap-[11px] items-center absolute top-[20px] left-[20px]">

      <img v-if="proirity" src="../public/img/alert-circle.svg" class="w-[29px] h-[29px]"/>

      <span class="w-[134px] h-[22px] font-semibold text-[16px] leading-[1] text-black font-open-sans">
        Смените пароль
      </span>

      <span class="w-[83px] h-[19px] font-semibold text-[14px] leading-[1] text-[#8A8A8A] font-open-sans">
        13 авг. 2024
      </span>
 
    </div>

    <div class="w-[270px] h-auto font-semibold text-[14px] leading-[1.1] text-[#8A8A8A] font-open-sans absolute left-[20px] top-[52px]">
      Мы рассмотрели вашу заявку и пришли к выводу, что данная позиция имеет место быть.
    </div>

    <Notification v-if="isRead" class="absolute z-100 top-[75px] right-[20px]"/>

  </div>
</template>

<script>

export default {

  props: {
    proirity: {
      type: Boolean,
      default: false
    },

    name: {
      default: 'Тестовое сообщение'
    },

    desc: {
      default: 'Это тестовое сообщение для отладки'
    },

    date: {
      default: '11.11.1111'
    },

    isRead: {
      type: Boolean,
      default: false
    }
  }
}

</script>

<style>

</style>