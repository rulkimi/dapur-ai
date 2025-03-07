import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import FontAwesomeIcon from './plugins/fontawesomeicons'
import { createPinia } from 'pinia'
import router from './routers'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')
