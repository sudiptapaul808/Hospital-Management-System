import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'

import { useUserStore } from './stores/user'
import '@mdi/font/css/materialdesignicons.css'

const app = createApp(App)

// const pinia = createPinia()
app.use(createPinia())
app.use(router)
app.use(vuetify)

const userStore = useUserStore()
userStore.loadFromStorage()

app.mount('#app')
