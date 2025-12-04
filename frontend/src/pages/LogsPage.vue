<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { IconCirclePlus, IconStar, IconBinoculars } from '@tabler/icons-vue'
import { request, deleteLog as apiDeleteLog } from '@/apiClient'

const logs = ref([])
const loading = ref(true)
const error = ref(null)
const router = useRouter()

async function fetchLogs() {
  loading.value = true
  error.value = null
  logs.value = []
  
  try {
    const data = await request('/api/logs/')
    logs.value = data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)

function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

async function deleteLog(id) {
  const ok = window.confirm('この観劇ログを削除しますか？')
  if (!ok) return

  await apiDeleteLog(id)

  // 再取得
  await fetchLogs()
}
</script>

<template>
  <main class="container py-4">
    <!-- <h1 class="mb-3 df-center">
      <img 
        src="/icon.svg"
        style="width: 80px;"
        alt="">
    </h1> -->

    <router-link to="/logs/new" class="btn text-dark df-center my-5">
      <IconCirclePlus :size="40"/>
    </router-link>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="error">エラー: {{ error }}</p>
    <div v-else-if="logs.length === 0">
      <div class="df-center text-center flex-column">
        その体験は<br>
        あなたの人生を豊かにします<br>
        <router-link to="/logs/new" class="mt-3">
          観劇を記録する
        </router-link>
      </div>
      
    </div>

    <div v-else class="row g-1">
      <div v-for="log in logs" :key="log.id" class="col-6 col-md-3 col-lg-2">
        <div class="poster position-relative">
          <router-link :to="`/logs/${log.id}/detail`">
            <img 
              v-if="log.work?.main_image || log.work?.main_image_url" 
              :src="log.work?.main_image || log.work?.main_image_url" 
              class="poster-img w-100"
              :alt="log.work.title"
              style="aspect-ratio: 1/1.414; object-fit: cover; cursor: pointer;"
            >
            <div 
              v-else 
              class="poster-img bg-secondary d-flex align-items-center justify-content-center text-white"
              style="aspect-ratio: 1/1.414; cursor: pointer;"
            >
              画像なし
            </div>
          </router-link>
          <div class="poster-body df-center gap-2 bg-light p-1">
            <div class="star df-center text-muted gap-1">
              <IconStar :size="16" />
              <div>{{ log.rating }}</div>
            </div>
            <div class="date df-center"><IconBinoculars :size="20" /><small>{{ formatDate(log.watchedDate) }}</small></div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>