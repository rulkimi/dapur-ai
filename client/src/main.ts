import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import FontAwesomeIcon from './plugins/fontawesomeicons'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)

app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')
