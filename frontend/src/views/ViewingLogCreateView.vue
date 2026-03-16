<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconTicket, IconStar } from '@tabler/icons-vue'
import Multiselect from '@vueform/multiselect'
import RatingButtons from '@/components/RatingButtons.vue'

const router = useRouter()
const route = useRoute()

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const performances = ref([])
const performance = ref(route.query.performance || '')
const status = ref(route.query.status || 'planned')
const watchedOn = ref(formatDate(new Date()))
const watchedTime = ref('13:00')
const memo = ref('')
const rating = ref('')
const spoiler = ref(false)
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

const perfOptions = computed(() =>
  performances.value.map((p) => ({ value: p.id, label: perfLabel(p) })),
)

function setDateOffset(offset) {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  watchedOn.value = formatDate(d)
}

const timePresets = ['13:00', '14:00', '18:00', '19:00']

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
      if (watchedTime.value) body.watched_time = watchedTime.value
    }
    await api.post('/api/viewing-logs/', body)
    // 感想があればレビューも同時作成
    if (memo.value.trim() && status.value === 'watched') {
      const reviewBody = {
        performance: Number(performance.value),
        body: memo.value,
        is_spoiler: spoiler.value,
      }
      if (rating.value) reviewBody.rating_overall = Number(rating.value)
      await api.post('/api/reviews/', reviewBody)
    }
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
    <header class="d-flex align-items-center justify-content-between pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0 small text-decoration-none" @click="router.back()">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </button>
      <h1 class="fs-6 fw-bold mb-0">記録する</h1>
      <div style="width: 48px"></div>
    </header>

    <div class="px-3 d-flex flex-column gap-4">
      <!-- 作品 / 公演選択 -->
      <div>
        <label class="form-label small text-secondary">作品 / 公演</label>
        <p v-if="perfLoading" class="small text-secondary">読み込み中...</p>
        <Multiselect
          v-else
          v-model="performance"
          :options="perfOptions"
          :searchable="true"
          placeholder="作品名・劇場名で検索..."
          no-results-text="該当する公演がありません"
          no-options-text="公演データがありません"
          class="multiselect-dark"
        >
          <template #noresults>
            <div class="px-3 py-2 text-center">
              <span class="small text-secondary">該当する公演がありません</span>
              <RouterLink to="/performances/new" class="d-block small mt-1 color-rose">公演を新しく追加する →</RouterLink>
            </div>
          </template>
        </Multiselect>
      </div>

      <!-- ステータス切替 -->
      <div>
        <label class="form-label small text-secondary">ステータス</label>
        <div class="d-flex gap-2">
          <button
            class="toggle-btn flex-fill fw-medium d-flex align-items-center justify-content-center"
            :class="{ 'is-active-light': status === 'planned' }"
            @click="status = 'planned'"
          >
            <IconTicket :size="16" class="me-1" />観る
          </button>
          <button
            class="toggle-btn flex-fill fw-medium d-flex align-items-center justify-content-center"
            :class="{ 'is-active-rose': status === 'watched' }"
            @click="status = 'watched'"
          >
            <IconStar :size="16" class="me-1" />観た
          </button>
        </div>
      </div>

      <!-- 観劇日時 -->
      <div v-if="status === 'watched'">
        <label class="form-label small text-secondary">観劇日</label>
        <div class="d-flex gap-2 mb-2">
          <button
            v-for="(offset, label) in { '昨日': -1, '今日': 0, '明日': 1 }"
            :key="label"
            class="toggle-btn flex-fill small"
            :class="{ 'is-active-light': watchedOn === formatDate(new Date(Date.now() + offset * 86400000)) }"
            @click="setDateOffset(offset)"
          >{{ label }}</button>
        </div>
        <div class="d-flex gap-2 mb-2">
          <button
            v-for="t in timePresets"
            :key="t"
            class="toggle-btn flex-fill small"
            :class="{ 'is-active-light': watchedTime === t }"
            @click="watchedTime = watchedTime === t ? '' : t"
          >{{ t }}</button>
        </div>
        <div class="d-flex gap-2">
          <input v-model="watchedOn" type="date" class="form-control bg-dark border-secondary text-light" />
          <input v-model="watchedTime" type="time" class="form-control bg-dark border-secondary text-light" style="max-width: 8rem" />
        </div>
      </div>

      <!-- 評価（観た時のみ） -->
      <div v-if="status === 'watched'">
        <label class="form-label small text-secondary">評価（任意）</label>
        <RatingButtons v-model="rating" />
      </div>

      <!-- メモ / 感想 -->
      <div>
        <label class="form-label small text-secondary">メモ / 感想</label>
        <textarea
          v-model="memo"
          rows="6"
          placeholder="観劇の感想やメモを書く..."
          class="form-control bg-dark border-secondary text-light"
        ></textarea>
      </div>

      <!-- ネタバレ（観た時のみ） -->
      <div v-if="status === 'watched'" class="form-check">
        <input v-model="spoiler" type="checkbox" class="form-check-input" id="spoilerCheck" />
        <label for="spoilerCheck" class="form-check-label small text-secondary">ネタバレを含む</label>
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

<style src="@vueform/multiselect/themes/default.css"></style>
<style scoped>
.toggle-btn {
  background: #444444;
  color: #a1a1aa;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;

  &.is-active-light {
    background: #ffffff;
    color: #000;
  }

  &.is-active-rose {
    background: #e11d48;
    color: #fff;
  }
}
.multiselect-dark {
  --ms-bg: #212529;
  --ms-border-color: #6c757d;
  --ms-color: #e4e4e7;
  --ms-placeholder-color: #a1a1aa;
  --ms-font-size: 0.875rem;
  --ms-line-height: 1.25;
  --ms-py: 0.375rem;
  --ms-px: 0.75rem;
  --ms-ring-color: rgba(244, 63, 94, 0.3);
  --ms-radius: 0.375rem;

  --ms-dropdown-bg: #212529;
  --ms-dropdown-border-color: #6c757d;
  --ms-dropdown-radius: 0.375rem;

  --ms-option-bg-pointed: #2d2d33;
  --ms-option-color-pointed: #e4e4e7;
  --ms-option-bg-selected: #e11d48;
  --ms-option-color-selected: #fff;
  --ms-option-bg-selected-pointed: #be123c;
  --ms-option-color-selected-pointed: #fff;
  --ms-option-font-size: 0.875rem;
  --ms-option-py: 0.5rem;
  --ms-option-px: 0.75rem;

  --ms-empty-color: #a1a1aa;

  --ms-tag-bg: #e11d48;
  --ms-tag-color: #fff;

  --ms-clear-color: #a1a1aa;
  --ms-clear-color-hover: #e4e4e7;
  --ms-caret-color: #a1a1aa;
  --ms-spinner-color: #e11d48;
}
</style>
