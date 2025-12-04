<!-- src/pages/LogEditPage.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '@/apiClient'
import { onLogSaveSuccess } from '@/lib/admobHelpers'

const route = useRoute()
const router = useRouter()
const id = computed(() => Number(route.params.id))

const loading = ref(true)
const error = ref(null)
const works = ref([])
const runs = ref([])

const form = ref({
  workId: '',
  runId: '',
  watchedDate: '',
  watchedTime: '',
  seat: '',
  memo: '',
  rating: '',
})

function formatDateInput(val) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

function formatTimeInput(val) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(11, 16) // HH:MM
}

async function fetchData() {
  loading.value = true
  try {
    // 作品一覧
    const worksData = await request('/api/works/')
    works.value = worksData

    // ログ一覧から該当の1件を引っこ抜く
    const all = await request('/api/logs/')
    const log = all.find((l) => l.id === id.value)
    if (!log) {
      throw new Error('ログが見つかりません')
    }

    // 作品詳細からRuns取得
    if (log.work) {
      const workDetail = await request(`/api/works/${log.work}/`)
      runs.value = workDetail.runs || []
    }

    form.value = {
      workId: log.work,
      runId: log.run || '',
      watchedDate: formatDateInput(log.watched_at),
      watchedTime: formatTimeInput(log.watched_at),
      seat: log.seat || '',
      memo: log.memo || '',
      rating: log.rating?.toString() || '',
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

async function handleSubmit(e) {
  e.preventDefault()

  // watched_atを日付+時間で構築
  let watchedAt = null
  if (form.value.watchedDate) {
    const time = form.value.watchedTime || '00:00'
    watchedAt = `${form.value.watchedDate}T${time}:00`
  }

  try {
    await request(`/api/logs/${id.value}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        work: Number(form.value.workId),
        run: form.value.runId ? Number(form.value.runId) : null,
        watched_at: watchedAt,
        seat: form.value.seat || null,
        memo: form.value.memo || null,
        rating: form.value.rating ? Number(form.value.rating) : null,
        tags: [],
      }),
    })

    // 更新成功：インタースティシャル広告を表示（3回に1回）
    await onLogSaveSuccess()

    router.push('/logs')
  } catch (error) {
    console.error('ログの更新に失敗しました:', error)
    alert('ログの更新に失敗しました。もう一度お試しください。')
  }
}
</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3">観劇ログを編集（Vue版）</h1>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="error">エラー: {{ error }}</p>

    <form v-else @submit="handleSubmit" class="mb-4">
      <div class="mb-3">
        <label class="form-label">作品</label>
        <select
          class="form-select"
          v-model="form.workId"
        >
          <option
            v-for="work in works"
            :key="work.id"
            :value="work.id"
          >
            {{ work.title }}（{{ work.main_theater?.name || work.theater?.name }}）
          </option>
        </select>
      </div>

      <div class="mb-3" v-if="runs.length > 0">
        <label class="form-label">公演ブロック（任意）</label>
        <select class="form-select" v-model="form.runId">
          <option value="">選択なし</option>
          <option
            v-for="run in runs"
            :key="run.id"
            :value="run.id"
          >
            {{ run.label }}（{{ run.area }}）
          </option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">観た日</label>
        <input
          type="date"
          class="form-control"
          v-model="form.watchedDate"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">時間（任意）</label>
        <input
          type="time"
          class="form-control"
          v-model="form.watchedTime"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">座席</label>
        <input
          type="text"
          class="form-control"
          v-model="form.seat"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">メモ</label>
        <textarea
          class="form-control"
          rows="3"
          v-model="form.memo"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">評価（1〜5）</label>
        <input
          type="number"
          min="1"
          max="5"
          class="form-control"
          v-model="form.rating"
        />
      </div>

      <button type="submit" class="btn btn-primary">更新</button>
    </form>
  </main>
</template>