<template>
  <div class="video-container">
    <video
      ref="videoPlayer"
      class="w-full rounded-lg shadow-lg"
      controls
      preload="metadata"
      @loadedmetadata="onVideoLoad"
    >
      <source :src="videoSrc" type="video/mp4">
      Ваш браузер не поддерживает воспроизведение видео.
    </video>
    
    <!-- Индикатор загрузки -->
    <div 
      v-if="loading" 
      class="absolute inset-0 flex items-center justify-center bg-gray-200 bg-opacity-50 rounded-lg"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  videoSrc: {
    type: String,
    required: true,
    default: '/public/example.mp4',
    validator: (value) => {
      // Базовая валидация URL
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    }
  }
});

const videoPlayer = ref(null);
const loading = ref(true);

const onVideoLoad = () => {
  loading.value = false;
};

// Автовоспроизведение при готовности (опционально)
onMounted(() => {
  if (videoPlayer.value) {
    videoPlayer.value.addEventListener('canplay', () => {
      loading.value = false;
    });
    
    videoPlayer.value.addEventListener('waiting', () => {
      loading.value = true;
    });
  }
});
</script>

<style scoped>
.video-container {
  position: relative;
  max-width: 100%;
  margin: 0 auto;
}

/* Адаптивные стили */
@media (max-width: 768px) {
  .video-container {
    max-width: 100%;
  }
}
</style>