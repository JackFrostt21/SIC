<template>
  <div class="md:w-[515px] w-full h-[116px] rounded-[10px] bg-white relative">

    <span class="md:w-[509.5px] h-[25px] font-semibold md:text-[18px] text-[16px] leading-[1] tracking-[0] text-black top-[20px] left-[20px] font-sans absolute" >
      Пароль
    </span>

    <div @click="openModal" class="flex flex-row w-[190px] h-[40px] rounded-[10px] bg-[#0C1E45] left-[20px] top-[59px] absolute">

      <span class="w-[82px] h-[22px] font-semibold md:text-[16px] text-[14px] leading-[1] text-white font-sans mt-[10px] ml-[56px]">
        Изменить
      </span>

    </div>

    <Test
      :is-visible="isModalVisible"
      @close="closeModal"
    >
    </Test>
    
  </div>
</template>

<script>

import Test from './Test.vue';
export default {
  components:{
    Test
  },
  data() {
    return {
      isModalVisible: false
    };
  },
  methods: {
    openModal() {
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    confirm() {
      alert('Действие подтверждено!');
      this.closeModal();
    }
  }
};


</script>

<style>

</style>