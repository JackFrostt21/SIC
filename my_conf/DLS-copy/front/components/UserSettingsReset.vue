<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">

    <p>ТЕСТ</p>

    <div 
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity duration-300"
      @click="closeModal"
    ></div>
    
  </div>
</template>

<script>

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Модальное окно'
    },
    showConfirmButton: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    closeModal() {
      this.$emit('update:isOpen', false);
    }
  }
}

</script>

<style>

</style>