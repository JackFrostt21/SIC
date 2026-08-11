<template>
  <div class="relative w-[691px] h-[461px] mx-auto bg-gray-900 rounded-lg overflow-hidden">
    <!-- Видео элемент -->
    <video
      v-if="!isAudio"
      ref="videoRef"
      class="w-full"
      :src="src"
      @timeupdate="updateProgress"
      @click="togglePlay"
    ></video>
    <audio 
      v-else
      ref="videoPlayer"
      class="w-full"
      @timeupdate="updateProgress"
      @loadedmetadata="updateDuration"
    >
      <source :src="src" type="audio/mpeg">
    </audio>

    <!-- Элементы управления -->
    <div 
      class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent"
      @click.stop
    >
      <!-- Прогресс бар -->
      <input
        type="range"
        v-model="progress"
        min="0"
        :max="duration"
        step="0.1"
        class="w-full h-1.5 mb-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
        @input="seekVideo"
      >

      <div class="flex items-center justify-between">
        <!-- Кнопки управления -->
        <div class="flex items-center space-x-4">
          <button @click="togglePlay" class="text-white hover:text-red-500">
            <img src="../public/img/stop.svg" v-if="isPlaying" />
            <img  v-else src="../public/img/play.svg" class="w-[12px] h-[12px]"/>
          </button>
          
          <span class="text-white text-sm">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>
        </div>

        <!-- Дополнительные элементы -->
        <div class="flex items-center space-x-3">
          <img src="../public/img/volume.svg">
          
          <input
            type="range"
            v-model="volume"
            min="0"
            max="1"
            step="0.1"
            class="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
            @input="setVolume"
          >
          
          <button @click="toggleFullscreen" class="text-white">
            ⛶
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFullscreen } from '@vueuse/core'

const props = defineProps({
  src: {
    type: String,
    required: true
  },

  isAudio: {type: Boolean, default: false}
})

const videoRef = ref(null)
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)
const volume = ref(0.7)

const { toggle: toggleFullscreen } = useFullscreen(videoRef)

onMounted(() => {
  videoRef.value.volume = volume.value
})

const togglePlay = () => {
  if (isPlaying.value) {
    videoRef.value.pause()
  } else {
    videoRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const toggleMute = () => {
  isMuted.value = !isMuted.value
  videoRef.value.muted = isMuted.value
}

const updateProgress = () => {
  currentTime.value = videoRef.value.currentTime
  progress.value = videoRef.value.currentTime
  duration.value = videoRef.value.duration || 0
}

const seekVideo = () => {
  videoRef.value.currentTime = progress.value
}

const setVolume = () => {
  videoRef.value.volume = volume.value
  if (volume.value === 0) {
    isMuted.value = true
  } else {
    isMuted.value = false
  }
}

const formatTime = (seconds) => {
  const date = new Date(0)
  date.setSeconds(seconds)
  return date.toISOString().substring(14, 19)
}
</script>

<style>
/* Стили для ползунков */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #FFFFFF;
  border-radius: 50%;
}

input[type="range"]::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #FFFFFF;
  border-radius: 50%;
  border: none;
}
</style>