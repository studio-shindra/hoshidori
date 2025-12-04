import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@/assets/styles/custom.scss'
import * as TablerIcons from '@tabler/icons-vue'
import { initAuth } from '@/authState'
import { createVfm } from 'vue-final-modal'
import 'vue-final-modal/style.css'

const app = createApp(App)
const vfm = createVfm()

// Tabler アイコン全登録（さっきのやつ）
for (const [name, component] of Object.entries(TablerIcons)) {
  app.component(name, component)
}

// 認証初期化してからマウント
initAuth().then(() => {
  app.use(router).use(vfm)
  .mount('#app')
})