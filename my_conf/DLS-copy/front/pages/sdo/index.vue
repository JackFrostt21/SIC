<template>
  <div class=".w-100 min-h-screen items-center flex flex-col items-center gap-[30px]">
    <Header />
    <Search @search="handleSearch" />
    <StatusBar />
    <div class="h-auto w-[90%] sm:w-[1040px] mx-auto flex flex-col gap-[30px]">
      <Nessary v-if="coursesLoaded" :items="filteredNessaryCourses"/>
      <NotCompleted v-if="coursesLoaded" :items="filteredAllCourses"/>
      <div v-else>Загрузка курсов...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCourses } from '#imports'
import { useUser } from '#imports'

const userCourse = useCourses()
const searchQuery = ref('')
const courses = ref({ all: [], nessary: [] })
const coursesLoaded = ref(false)

// Реактивные версии списков курсов
const allCourses = ref([])
const nessaryCourses = ref([])

onMounted(async () => {
  try {
    console.log('Начало загрузки курсов')
    const feedback = await userCourse.getCourses()
    allCourses.value = feedback.all || []
    nessaryCourses.value = feedback.nessary || []
    coursesLoaded.value = true
    console.log('Курсы успешно загружены:', {
      all: allCourses.value,
      nessary: nessaryCourses.value
    })
    
    const getUser = useUser()
    await getUser.getUser()
  } catch (error) {
    console.error('Ошибка загрузки курсов:', error)
  }
})

const filterCourses = (coursesList) => {
  if (!searchQuery.value.trim()) {
    console.log('Пустой запрос - возвращаем все курсы', coursesList)
    return coursesList
  }

  const queryLower = searchQuery.value.toLowerCase()
  const filtered = coursesList.filter(course => 
    course.title?.toLowerCase().includes(queryLower) ||
    course.name?.toLowerCase().includes(queryLower) ||
    course.description?.toLowerCase().includes(queryLower)
  )
  
  console.log('Отфильтрованные курсы по запросу', searchQuery.value, filtered)
  return filtered
}

// Отдельные computed свойства для каждого списка
const filteredAllCourses = computed(() => {
  console.log('Обновление списка всех курсов')
  return filterCourses(allCourses.value)
})

const filteredNessaryCourses = computed(() => {
  console.log('Обновление списка обязательных курсов')
  return filterCourses(nessaryCourses.value)
})

const handleSearch = (query) => {
  console.log('Получен новый поисковый запрос:', query)
  searchQuery.value = query
}
</script>

<style>
body {
  background: #F2F2F2;
}
</style>