<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/lib/api'
import { IconTicket, IconClick, IconReceipt } from '@tabler/icons-vue'

const data = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await api.get('/api/dashboard/')
  } catch (e) {
    if (e.status === 404) {
      error.value = '店舗が登録されていません'
    } else if (e.status === 403) {
      error.value = 'アクセス権限がありません'
    } else {
      error.value = 'データを取得できませんでした'
    }
  } finally {
    loading.value = false
  }
})

const maxDaily = computed(() => {
  if (!data.value?.daily_coupon_use_counts) return 1
  const max = Math.max(...data.value.daily_coupon_use_counts.map((d) => d.count))
  return max || 1
})

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<template>
  <div>
    <header class="pt-4 pb-3">
      <h1 class="fs-5 fw-bold mb-0">店舗ダッシュボード</h1>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <div v-else-if="error" class="px-3">
      <div class="card bg-dark border-0 p-4 text-center">
        <p class="text-danger mb-0">{{ error }}</p>
      </div>
    </div>
    <template v-else-if="data">
      <div class="px-3">
        <p class="small text-secondary mb-3">{{ data.shop_name }}</p>

        <!-- Stats grid -->
        <div class="row g-2 mb-4">
          <div class="col-6">
            <div class="card bg-dark border-0 p-3 text-center">
              <div class="tiny text-secondary mb-1"><IconTicket :size="12" class="me-1" />クーポン利用 総数</div>
              <div class="fs-3 fw-bold color-rose">{{ data.coupon_use_total }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="card bg-dark border-0 p-3 text-center">
              <div class="tiny text-secondary mb-1"><IconTicket :size="12" class="me-1" />クーポン利用 今日</div>
              <div class="fs-3 fw-bold color-amber">{{ data.coupon_use_today }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="card bg-dark border-0 p-3 text-center">
              <div class="tiny text-secondary mb-1"><IconClick :size="12" class="me-1" />クリック 総数</div>
              <div class="fs-3 fw-bold text-light">{{ data.click_total }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="card bg-dark border-0 p-3 text-center">
              <div class="tiny text-secondary mb-1"><IconClick :size="12" class="me-1" />クリック 今日</div>
              <div class="fs-3 fw-bold text-light">{{ data.click_today }}</div>
            </div>
          </div>
        </div>

        <!-- Daily chart (bar-style with progress) -->
        <section v-if="data.daily_coupon_use_counts?.length" class="mb-4">
          <h3 class="small fw-semibold text-secondary mb-3">直近7日のクーポン利用</h3>
          <div class="d-flex flex-column gap-2">
            <div v-for="d in data.daily_coupon_use_counts" :key="d.date" class="d-flex align-items-center gap-2">
              <span class="tiny text-secondary" style="width: 36px">{{ formatDate(d.date) }}</span>
              <div class="flex-grow-1">
                <div class="progress" style="height: 18px; background: #27272a">
                  <div
                    class="progress-bar"
                    role="progressbar"
                    :style="{ width: (d.count / maxDaily * 100) + '%', background: '#e11d48' }"
                  ></div>
                </div>
              </div>
              <span class="tiny text-light fw-medium" style="width: 24px; text-align: right">{{ d.count }}</span>
            </div>
          </div>
        </section>

        <!-- Recent uses -->
        <section v-if="data.recent_coupon_uses?.length" class="mb-5">
          <h3 class="small fw-semibold text-secondary mb-3">
            <IconReceipt :size="14" class="me-1" />直近のクーポン利用
          </h3>
          <div class="d-flex flex-column gap-2">
            <div v-for="u in data.recent_coupon_uses" :key="u.id" class="card bg-dark border-0 p-3">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="small fw-medium text-light">{{ u.coupon_title }}</div>
                  <div v-if="u.performance_id" class="tiny text-secondary">公演ID: {{ u.performance_id }}</div>
                </div>
                <span class="tiny text-secondary">{{ new Date(u.used_at).toLocaleString('ja-JP', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
