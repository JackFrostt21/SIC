<template>
  <div class="pdf-viewer">
    <div class="controls">
      <button @click="prevPage" :disabled="pageNumber <= 1">Назад</button>
      <span>Страница {{ pageNumber }} из {{ numPages }}</span>
      <button @click="nextPage" :disabled="pageNumber >= numPages">Вперёд</button>
    </div>
    
    <div class="canvas-container">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  }
})

const canvas = ref(null)
const pdfDoc = ref(null)
const pageNumber = ref(1)
const numPages = ref(0)
const renderTask = ref(null)

// Инициализация PDF.js
const loadPDF = async () => {
  try {
    const pdfjsLib = await import('pdfjs-dist/build/pdf')
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/js/pdf.worker.min.js'
    
    const loadingTask = pdfjsLib.getDocument(props.src)
    pdfDoc.value = await loadingTask.promise
    numPages.value = pdfDoc.value.numPages
    renderPage(pageNumber.value)
  } catch (error) {
    console.error('Ошибка загрузки PDF:', error)
  }
}

const renderPage = async (num) => {
  if (!pdfDoc.value) return
  
  // Очистка canvas перед рендером
  const context = canvas.value.getContext('2d')
  context.clearRect(0, 0, canvas.value.width, canvas.value.height)
  
  try {
    const page = await pdfDoc.value.getPage(num)
    const viewport = page.getViewport({ scale: 1.5 })
    
    canvas.value.height = viewport.height
    canvas.value.width = viewport.width
    
    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }
    
    // Используем await без сохранения task
    await page.render(renderContext).promise
    
  } catch (error) {
    if (error.message !== 'Rendering cancelled') {
      console.error('Render error:', error)
    }
  }
}

// Навигация по страницам
const nextPage = () => {
  if (pageNumber.value < numPages.value) {
    pageNumber.value++
  }
}

const prevPage = () => {
  if (pageNumber.value > 1) {
    pageNumber.value--
  }
}

// Отслеживание изменения страницы
watch(pageNumber, (newPage) => {
  renderPage(newPage)
})

// Отслеживание изменения источника PDF
watch(() => props.src, () => {
  loadPDF()
})

onMounted(() => {
  loadPDF()
})

onUnmounted(() => {
  if (renderTask.value) {
    renderTask.value.cancel()
  }
})
</script>

<style scoped>
.pdf-viewer {
  max-width: 100%;
  margin: 0 auto;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.canvas-container {
  display: flex;
  justify-content: center;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: auto;
}

canvas {
  max-width: 100%;
}
</style>