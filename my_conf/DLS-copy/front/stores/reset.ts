import { defineStore } from 'pinia'

export const useResetStore = defineStore('reset', {
  state: () => ({
    email: null as string | null,
    token: null as string | null,
    new_password: null as string | null,
    confrim_password: null as string | null
  }),
  actions: {
    setEmail (email: string){
      this.email = email
    },
    setToken (token: string){
      this.token = token
    },
    setPassword(new_password: string, confrim_password: string){
      this.new_password = new_password,
      this.confrim_password = confrim_password
    }
  },
  persist: true,
})
