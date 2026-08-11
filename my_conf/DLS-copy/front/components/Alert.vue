<template>
  <div 
    v-if="visible"
    class="fixed md:absolute top-0 md:top-[70px] left-0 md:right-[40px] w-full md:w-[515px] bg-white rounded-none md:rounded-bl-[10px] md:rounded-br-[10px] shadow-lg md:shadow-[8px_-7px_16.9px_0_rgba(0,0,0,0.1)] p-4 md:p-5 transition-all duration-300 z-50"
    :class="{
      'animate-notification-enter': isMounted && visible,
      'animate-notification-leave': !visible
    }"
  >
    <div class="flex gap-3 md:gap-4">
      <img src="../public/img/alert-circle.svg" class="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div class="font-semibold text-sm md:text-base text-black font-open-sans flex-1">
        {{message}}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const visible = ref(true);
const isMounted = ref(false);

const props = defineProps({
  message: {
    type: String,
    required: true,
    default: 'Это тестовое сообщение'
  },
  duration: {
    type: Number,
    default: 10000 // 10 секунд по умолчанию
  }
});

onMounted(() => {
  isMounted.value = true;

  setTimeout(() => {
    visible.value = false;
  }, props.duration);
});
</script>

<style>
@keyframes notification-enter {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes notification-leave {
  to {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
}

.animate-notification-enter {
  animation: notification-enter 0.3s ease-out forwards;
}

.animate-notification-leave {
  animation: notification-leave 0.3s ease-in forwards;
}
</style>