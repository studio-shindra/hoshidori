import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@/assets/styles/custom.scss'
import * as TablerIcons from '@tabler/icons-vue'
import { initAuth } from '@/authState'

const app = createApp(App)

// Tabler アイコン全登録（さっきのやつ）
for (const [name, component] of Object.entries(TablerIcons)) {
  app.component(name, component)
}

// 認証初期化してからマウント
initAuth().then(() => {
  app.use(router).mount('#app')
})