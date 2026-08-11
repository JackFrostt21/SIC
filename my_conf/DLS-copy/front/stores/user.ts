import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    is_actual: null as boolean | null,
    state: null as string | null,
    full_name: null as string | null,
    last_name: null as string | null,
    first_name: null as string | null,
    middle_name: null as string | null,
    date_of_birth: null as string | null,
    email: null as string | null,
    phone: null as string | null,
    language: null as string | null,
    image: null as string | null,
    company: null as string | null,
    departament: null as string | null,
    job_title: null as string | null
  }),
  actions: {
    setUser(is_actual: boolean, 
      state: string, full_name: string, 
      last_name: string, first_name: string, 
      middle_name: string, date_of_birth: string,
      email: string, phone: string, language: string,
      image: string, company: string, departament: string,
      job_title: string) 
      {
        this.is_actual = is_actual
        this.state = state
        this.full_name = full_name
        this.last_name = last_name
        this.first_name = first_name
        this.middle_name = middle_name
        this.date_of_birth = date_of_birth
        this.email = email
        this.phone = phone
        this.language = language
        this.image = image
        this.company = company
        this.departament = departament
        this.job_title = job_title
  },
    clearUser() {
      this.is_actual = null
      this.state = null
      this.full_name = null
      this.last_name = null
      this.first_name = null
      this.middle_name = null
      this.date_of_birth = null
      this.email = null
      this.phone = null
      this.language = null
      this.image = null
      this.company = null
      this.departament = null
      this.job_title = null
      this.image = null
    },
    
    setAvatar(image: string) {
      this.image = image
    }
},
persist: true,
})
