import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'


const app = createApp(App)

app.use(createPinia())
app.use(router)

axios.defaults.baseURL = 'https://d5ptpgq7oh.execute-api.eu-west-3.amazonaws.com/prod'
axios.defaults.withCredentials = true

// Request interceptor
axios.interceptors.request.use((config) => {
    // Modify the request config here
    return config
  })

app.config.globalProperties.$axios = axios


app.mount('#app')
