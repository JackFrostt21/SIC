import { defineStore } from 'pinia'

export const useCoursesStore = defineStore('courses', {
  state: () => ({
    courses: [],
    topics: []
  }),
  actions: {
    setCourses (courses: any){
      this.courses = courses
    },
    setTopics (topics: any) {
      this.topics = topics
    }
  },
  persist: true,
})
