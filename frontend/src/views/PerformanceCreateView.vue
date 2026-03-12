<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft } from '@tabler/icons-vue'

const router = useRouter()
const works = ref([])
const theaters = ref([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref(false)

const form = ref({
  work: '',
  theater: '',
  company_name: '',
  start_date: '',
  end_date: '',
  note: '',
})

onMounted(async () => {
  try {
    const [wData, tData] = await Promise.all([
      api.get('/api/works/'),
      api.get('/api/theaters/'),
    ])
    works.value = wData.results || wData
    theaters.value = tData.results || tData
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!form.value.work || !form.value.theater || !form.value.start_date || !form.value.end_date) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/api/performances/', {
      work: Number(form.value.work),
      theater: Number(form.value.theater),
      company_name: form.value.company_name,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      note: form.value.note,
    })
    success.value = true
    form.value = { work: '', theater: '', company_name: '', start_date: '', end_date: '', note: '' }
  } catch (e) {
    error.value = e.data ? Object.values(e.data).flat().join(' ') : '作成に失敗しました'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center gap-2 px-3 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">公演を追加</h1>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <form v-else @submit.prevent="submit" class="px-3 d-flex flex-column gap-3">
      <div>
        <label class="form-label tiny text-secondary">作品 *</label>
        <select v-model="form.work" required class="form-select bg-dark border-secondary text-light">
          <option value="" disabled>選択してください</option>
          <option v-for="w in works" :key="w.id" :value="w.id">{{ w.title }}</option>
        </select>
        <RouterLink to="/works/new" class="tiny text-secondary">作品が見つからない場合 →</RouterLink>
      </div>
      <div>
        <label class="form-label tiny text-secondary">劇場 *</label>
        <select v-model="form.theater" required class="form-select bg-dark border-secondary text-light">
          <option value="" disabled>選択してください</option>
          <option v-for="t in theaters" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <div>
        <label class="form-label tiny text-secondary">カンパニー名（任意）</label>
        <input v-model="form.company_name" type="text" placeholder="劇団名など" class="form-control bg-dark border-secondary text-light" />
      </div>
      <div class="row g-2">
        <div class="col-6">
          <label class="form-label tiny text-secondary">開始日 *</label>
          <input v-model="form.start_date" type="date" required class="form-control bg-dark border-secondary text-light" />
        </div>
        <div class="col-6">
          <label class="form-label tiny text-secondary">終了日 *</label>
          <input v-model="form.end_date" type="date" required class="form-control bg-dark border-secondary text-light" />
        </div>
      </div>
      <div>
        <label class="form-label tiny text-secondary">メモ（任意）</label>
        <textarea v-model="form.note" rows="2" placeholder="補足情報" class="form-control bg-dark border-secondary text-light"></textarea>
      </div>
      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <div v-if="success" class="small color-green">公演を追加しました！</div>
      <button type="submit" :disabled="submitting" class="btn btn-primary-rose w-100 fw-medium py-2 mb-4">
        {{ submitting ? '追加中...' : '公演を追加' }}
      </button>
    </form>
  </div>
</template>
