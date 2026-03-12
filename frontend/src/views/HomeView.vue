<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import { IconSearch, IconMask, IconMessageCircle } from '@tabler/icons-vue'

const auth = useAuthStore()
const loading = ref(true)
const plannedLogs = ref([])
const watchedLogs = ref([])
const reviews = ref([])

const plannedCount = computed(() => plannedLogs.value.length)
const watchedCount = computed(() => watchedLogs.value.length)
const reviewCount = computed(() => reviews.value.length)

onMounted(async () => {
  if (!auth.isAuthenticated) {
    loading.value = false
    return
  }
  try {
    const [pData, wData, rData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
      api.get('/api/reviews/'),
    ])
    plannedLogs.value = pData.results || pData
    watchedLogs.value = wData.results || wData
    reviews.value = rData.results || rData
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- Header -->
    <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-2">
      <h1 class="fs-4 fw-bold mb-0 brand-title">HOSHIDORI</h1>
      <RouterLink to="/works" class="btn btn-link text-secondary p-0">
        <IconSearch :size="20" />
      </RouterLink>
    </header>

    <!-- Quick search -->
    <div class="px-3 mb-3">
      <div class="d-flex gap-2">
        <RouterLink to="/works" class="btn btn-dark btn-sm flex-fill text-start">
          <IconSearch :size="14" class="me-1 text-secondary" />作品を検索
        </RouterLink>
        <RouterLink to="/theaters" class="btn btn-dark btn-sm flex-fill text-start">
          <IconSearch :size="14" class="me-1 text-secondary" />劇場を検索
        </RouterLink>
      </div>
    </div>

    <!-- Not logged in -->
    <template v-if="!auth.isAuthenticated">
      <div class="px-3 py-5 text-center">
        <IconMask :size="48" class="text-secondary mb-3" />
        <p class="text-secondary mb-3">あなたの観劇体験を記録しよう</p>
        <div class="d-flex gap-2 justify-content-center">
          <RouterLink to="/login" class="btn btn-primary-rose px-4">ログイン</RouterLink>
          <RouterLink to="/register" class="btn btn-dark px-4">新規登録</RouterLink>
        </div>
        <div class="mt-4">
          <RouterLink to="/works" class="text-secondary small">作品を探す →</RouterLink>
        </div>
      </div>
    </template>

    <!-- Logged in -->
    <template v-else>
      <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
      <template v-else>
        <!-- Stats cards -->
        <div class="row g-2 px-3 mb-4">
          <div class="col-4">
            <div class="card bg-dark border-0 text-center py-3">
              <div class="fs-3 fw-bold color-amber">{{ plannedCount }}</div>
              <div class="small text-secondary">これから観る</div>
            </div>
          </div>
          <div class="col-4">
            <div class="card bg-dark border-0 text-center py-3">
              <div class="fs-3 fw-bold color-green">{{ watchedCount }}</div>
              <div class="small text-secondary">観た</div>
            </div>
          </div>
          <div class="col-4">
            <div class="card bg-dark border-0 text-center py-3">
              <div class="fs-3 fw-bold text-light">{{ reviewCount }}</div>
              <div class="small text-secondary">感想</div>
            </div>
          </div>
        </div>

        <!-- これから観る -->
        <section v-if="plannedLogs.length" class="mb-4">
          <h2 class="small fw-semibold text-secondary px-3 mb-3">これから観る</h2>
          <div class="d-flex gap-3 px-3 overflow-auto scroll-hide">
            <div v-for="log in plannedLogs" :key="log.id" class="card-sm">
              <div class="poster-sm poster-empty d-flex flex-column align-items-center justify-content-center gap-1">
                <IconMask :size="24" class="text-secondary" />
                <span class="tiny text-secondary">ポスター画像募集中</span>
              </div>
              <div class="mt-2">
                <div class="small fw-medium text-truncate">{{ log.performance_display || '公演' }}</div>
                <span class="badge badge-amber mt-1">これから観る</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 最近観た作品 -->
        <section v-if="watchedLogs.length" class="mb-4">
          <h2 class="small fw-semibold text-secondary px-3 mb-3">最近観た作品</h2>
          <div class="d-flex flex-column gap-3 px-3">
            <div v-for="log in watchedLogs" :key="log.id" class="card bg-dark border-0 p-3">
              <div class="d-flex gap-3">
                <div class="thumb poster-empty d-flex align-items-center justify-content-center">
                  <IconMask :size="18" class="text-secondary" />
                </div>
                <div class="flex-grow-1 min-w-0">
                  <div class="fw-medium small text-truncate">{{ log.performance_display || '公演' }}</div>
                  <div class="tiny text-secondary mt-1" v-if="log.watched_on">{{ log.watched_on }}</div>
                  <div class="d-flex align-items-center gap-2 mt-1">
                    <span class="badge badge-green">観た</span>
                  </div>
                  <div v-if="log.memo" class="tiny text-secondary mt-1 text-truncate">{{ log.memo }}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 空の場合 -->
        <div v-if="!plannedLogs.length && !watchedLogs.length" class="px-3 py-4 text-center">
          <IconMessageCircle :size="36" class="text-secondary mb-2" />
          <p class="text-secondary small">まだ記録がありません</p>
          <RouterLink to="/works" class="btn btn-primary-rose btn-sm px-3">作品を探す</RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.brand-title {
  letter-spacing: 0.05em;
}
.card-sm {
  flex-shrink: 0;
  width: 140px;
}
.poster-sm {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  overflow: hidden;
  padding: 8px;
}
.thumb {
  width: 56px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 8px;
}
</style>
