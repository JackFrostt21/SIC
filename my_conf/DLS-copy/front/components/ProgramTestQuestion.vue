<template>
  <div>
      <div class="w-[637px] mt-[20px] ml-[20px]">
        <p class="font-sans font-semibold text-[18px] leading-[110%] tracking-[0%] text-[#000000]">
          Обязан ли водитель перед началом эксплуатации транспортного средства осмотреть его?
        </p>
      </div>

      <div class="ml-[20px] mt-[10px] font-open-sans font-semibold text-sm leading-none tracking-normal text-[#8A8A8A]">
        Выберите один вариант ответа
      </div>

      <div class="ml-[20px] mt-[26px] mb-[50px] flex flex-col h-auto flex-items gap-[15.88px] w-[673px]">

        <ProgramTestAnswer />
        <ProgramTestAnswer answ="Нет"/>
        <ProgramTestAnswer answ="Затрудняюсь ответить"/>

      </div>
    </div>
</template>

<script lang="ts" setup>

</script>

<style>

</style>