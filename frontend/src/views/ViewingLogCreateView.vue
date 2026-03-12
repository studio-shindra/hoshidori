<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft } from '@tabler/icons-vue'

const router = useRouter()
const route = useRoute()

const performances = ref([])
const performance = ref(route.query.performance || '')
const status = ref(route.query.status || 'planned')
const watchedOn = ref('')
const memo = ref('')
const error = ref('')
const loading = ref(false)
const perfLoading = ref(true)

onMounted(async () => {
  try {
    const data = await api.get('/api/performances/')
    performances.value = data.results || data
  } catch {
    /* empty */
  } finally {
    perfLoading.value = false
  }
})

function perfLabel(p) {
  const parts = []
  if (p.work_title || p.work_name) parts.push(p.work_title || p.work_name)
  if (p.theater_name) parts.push(p.theater_name)
  if (p.start_date) parts.push(p.start_date)
  return parts.length ? parts.join(' / ') : `公演 #${p.id}`
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const body = {
      performance: Number(performance.value),
      status: status.value,
      memo: memo.value,
    }
    if (status.value === 'watched' && watchedOn.value) {
      body.watched_on = watchedOn.value
    }
    await api.post('/api/viewing-logs/', body)
    router.push('/logs')
  } catch (e) {
    const d = e.data
    if (d) {
      error.value = Object.values(d).flat().join(' ')
    } else {
      error.value = '保存に失敗しました'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0 small text-decoration-none" @click="router.back()">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </button>
      <h1 class="fs-6 fw-bold mb-0">記録する</h1>
      <div style="width: 48px"></div>
    </header>

    <div class="px-3 d-flex flex-column gap-4">
      <!-- 作品 / 公演選択 -->
      <div>
        <label class="form-label tiny text-secondary">作品 / 公演</label>
        <p v-if="perfLoading" class="tiny text-secondary">読み込み中...</p>
        <select v-else v-model="performance" required class="form-select bg-dark border-secondary text-light">
          <option value="" disabled>作品を選択</option>
          <option v-for="p in performances" :key="p.id" :value="p.id">
            {{ perfLabel(p) }}
          </option>
        </select>
      </div>

      <!-- ステータス切替 -->
      <div>
        <label class="form-label tiny text-secondary">ステータス</label>
        <div class="d-flex gap-2">
          <button
            class="btn flex-fill fw-medium"
            :class="status === 'planned' ? 'btn-status-amber' : 'btn-dark text-secondary'"
            @click="status = 'planned'"
          >
            これから観る
          </button>
          <button
            class="btn flex-fill fw-medium"
            :class="status === 'watched' ? 'btn-status-green' : 'btn-dark text-secondary'"
            @click="status = 'watched'"
          >
            観た
          </button>
        </div>
      </div>

      <!-- 観劇日 -->
      <div v-if="status === 'watched'">
        <label class="form-label tiny text-secondary">観劇日</label>
        <input v-model="watchedOn" type="date" class="form-control bg-dark border-secondary text-light" />
      </div>

      <!-- メモ / 感想 -->
      <div>
        <label class="form-label tiny text-secondary">メモ / 感想</label>
        <textarea
          v-model="memo"
          rows="6"
          placeholder="観劇の感想やメモを書く..."
          class="form-control bg-dark border-secondary text-light"
        ></textarea>
      </div>

      <!-- Error -->
      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>

      <!-- Buttons -->
      <div class="d-flex gap-2 mt-2 mb-5">
        <button class="btn btn-dark flex-fill fw-medium text-secondary" disabled>下書き保存</button>
        <button class="btn btn-primary-rose flex-fill fw-medium" :disabled="loading" @click="submit">
          {{ loading ? '保存中...' : '投稿する' }}
        </button>
      </div>
    </div>
  </div>
</template>
