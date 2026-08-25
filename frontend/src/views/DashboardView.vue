<script setup>
import { computed, onMounted, ref } from 'vue'
import { IconArrowLeft, IconClick, IconSparkles, IconStarFilled } from '@tabler/icons-vue'
import { api } from '@/lib/api'
import { RouterLink } from 'vue-router'

const data = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await api.get('/api/dashboard/')
  } catch (requestError) {
    if (requestError.status === 404) error.value = '店舗が登録されていません'
    else if (requestError.status === 403) error.value = 'アクセス権限がありません'
    else error.value = 'データを取得できませんでした'
  } finally {
    loading.value = false
  }
})

const maxDaily = computed(() => {
  const counts = data.value?.daily_after_viewing_counts || []
  return Math.max(...counts.map((day) => day.count), 1)
})

function formatDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<template>
  <div class="pb-5">
    <header class="d-flex align-items-center justify-content-between pt-4 pb-3">
      <RouterLink to="/mypage" class="btn btn-link text-secondary p-0 small text-decoration-none page-back">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </RouterLink>
      <h1 class="fs-6 fw-bold mb-0">店舗向け送客レポート</h1>
      <div class="page-back-spacer"></div>
    </header>
    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <div v-else-if="error" class="card bg-dark border-0 p-4 text-center"><p class="text-danger mb-0">{{ error }}</p></div>
    <template v-else-if="data">
      <p class="small text-secondary mb-3">{{ data.shop_name }}</p>
      <div class="row g-2 mb-4">
        <div class="col-6">
          <div class="stat-card">
            <div class="tiny text-secondary"><IconStarFilled :size="12" />感想戦に選ばれた総数</div>
            <div class="fs-3 fw-bold color-rose">{{ data.after_viewing_total }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="stat-card">
            <div class="tiny text-secondary"><IconSparkles :size="12" />今月</div>
            <div class="fs-3 fw-bold color-amber">{{ data.after_viewing_this_month }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="stat-card">
            <div class="tiny text-secondary"><IconClick :size="12" />店舗ページ総クリック</div>
            <div class="fs-3 fw-bold">{{ data.click_total }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="stat-card">
            <div class="tiny text-secondary"><IconClick :size="12" />今日のクリック</div>
            <div class="fs-3 fw-bold">{{ data.click_today }}</div>
          </div>
        </div>
      </div>

      <section v-if="data.daily_after_viewing_counts?.length" class="report-card mb-4">
        <h2 class="small fw-semibold mb-3">直近7日の「その後行った店」登録</h2>
        <div class="d-flex flex-column gap-2">
          <div v-for="day in data.daily_after_viewing_counts" :key="day.date" class="d-flex align-items-center gap-2">
            <span class="tiny text-secondary date-label">{{ formatDate(day.date) }}</span>
            <div class="flex-grow-1 progress" style="height: 16px; background: #27272a">
              <div class="progress-bar" :style="{ width: `${day.count / maxDaily * 100}%`, background: '#f43f5e' }"></div>
            </div>
            <span class="tiny text-end count-label">{{ day.count }}</span>
          </div>
        </div>
      </section>

      <section v-if="data.top_works?.length" class="report-card">
        <h2 class="small fw-semibold mb-3">どの作品のあとに選ばれたか</h2>
        <div v-for="work in data.top_works" :key="work.work_title" class="d-flex align-items-center justify-content-between py-2 border-top border-secondary">
          <span class="small text-truncate">{{ work.work_title }}</span>
          <strong class="color-rose ms-3">{{ work.count }}</strong>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.stat-card, .report-card { height: 100%; padding: 14px; border: 1px solid rgba(255,255,255,.09); border-radius: 13px; background: #18181b; }
.stat-card .tiny { display: flex; align-items: center; justify-content: center; gap: 4px; text-align: center; }
.stat-card { text-align: center; }
.date-label { width: 36px; }
.count-label { width: 20px; }
</style>
