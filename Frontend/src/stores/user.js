import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {  //creates global store
  state: () => ({  //the state
    user: null,
    token: null
  }),
  actions: {   //the actions on the state
    setUser(data) {
      this.user = {
        role: data.role
      }
      this.token = data.access_token

      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
    },

    loadFromStorage() {  //This is run on main.js. Why main.js? Cause main.js is run everytime the app runs, ie, even when the user uses refresh
      this.token = localStorage.getItem('token')
      this.user = {
        role: localStorage.getItem('role')
      }
    },

    logout() {
      this.user = null
      this.token = null

      localStorage.removeItem('token')
      localStorage.removeItem('role')
    }
  }
})


//The below two lines is what we need to access this store in a component
// import { useUserStore } from '../stores/user'
// const userStore = useUserStore()

//Here we're storing the token in pinia as well as the local storage but pinia will lose the information as soon as the user hits refresh and what happens then? the main.js is run and the loadFromStorage() is run there and pinia has the information it needs again. 