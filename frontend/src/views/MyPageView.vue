<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { IconStar, IconHeart, IconEye, IconCalendar, IconPhoto, IconMessage } from '@tabler/icons-vue'

const auth = useAuthStore()
const router = useRouter()

const planned = ref([])
const watched = ref([])
const myReviews = ref([])
const myPosters = ref([])
const activeTab = ref('planned')
const loading = ref(true)

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage' } })
    return
  }
  try {
    const [pData, wData, rData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
      api.get('/api/reviews/'),
    ])
    planned.value = pData.results || pData
    watched.value = wData.results || wData
    const allReviews = rData.results || rData
    const me = auth.user
    myReviews.value = allReviews.filter(
      (r) => r.user === me.username,
    )
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return ''
  return d.replace(/-/g, '.')
}

async function logout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="px-3 pt-4 pb-3">
    <!-- Header -->
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h2 class="fs-5 fw-bold mb-0">観劇棚</h2>
        <RouterLink to="/mypage/edit" class="btn btn-sm btn-dark text-secondary">編集</RouterLink>
      </div>
      <div class="d-flex align-items-baseline gap-2 mb-1">
        <span class="fw-semibold">{{ auth.user?.display_name || auth.user?.username }}</span>
        <span class="small text-secondary">@{{ auth.user?.username }}</span>
      </div>
      <p v-if="auth.user?.bio" class="small text-secondary mb-1">{{ auth.user.bio }}</p>
      <p class="tiny text-secondary mb-0">観た舞台や、これから観る舞台をまとめた自分の棚</p>
    </div>

    <p v-if="loading" class="text-secondary text-center py-5">読み込み中...</p>

    <template v-else>
      <!-- Summary Cards -->
      <div class="row g-2 mb-4">
        <div class="col-3">
          <button class="card bg-dark border-0 text-center py-3 w-100 btn p-0"
                  :class="{ 'border-warning': activeTab === 'planned' }"
                  :style="activeTab === 'planned' ? 'border: 1px solid #f59e0b !important' : ''"
                  @click="activeTab = 'planned'">
            <div class="fs-4 fw-bold" style="color: #f59e0b;">{{ planned.length }}</div>
            <div class="tiny text-secondary">これから</div>
          </button>
        </div>
        <div class="col-3">
          <button class="card bg-dark border-0 text-center py-3 w-100 btn p-0"
                  :class="{ 'border-success': activeTab === 'watched' }"
                  :style="activeTab === 'watched' ? 'border: 1px solid #22c55e !important' : ''"
                  @click="activeTab = 'watched'">
            <div class="fs-4 fw-bold" style="color: #22c55e;">{{ watched.length }}</div>
            <div class="tiny text-secondary">観た</div>
          </button>
        </div>
        <div class="col-3">
          <button class="card bg-dark border-0 text-center py-3 w-100 btn p-0"
                  :class="{ 'border-light': activeTab === 'reviews' }"
                  :style="activeTab === 'reviews' ? 'border: 1px solid #a1a1aa !important' : ''"
                  @click="activeTab = 'reviews'">
            <div class="fs-4 fw-bold text-light">{{ myReviews.length }}</div>
            <div class="tiny text-secondary">感想</div>
          </button>
        </div>
        <div class="col-3">
          <button class="card bg-dark border-0 text-center py-3 w-100 btn p-0"
                  :class="{ 'border-info': activeTab === 'posters' }"
                  :style="activeTab === 'posters' ? 'border: 1px solid #38bdf8 !important' : ''"
                  @click="activeTab = 'posters'">
            <div class="fs-4 fw-bold" style="color: #38bdf8;">{{ myPosters.length }}</div>
            <div class="tiny text-secondary">ポスター</div>
          </button>
        </div>
      </div>

      <!-- Tab: これから観る -->
      <section v-if="activeTab === 'planned'">
        <h3 class="small fw-semibold text-secondary mb-3">
          <IconCalendar :size="14" class="me-1" />これから観る
        </h3>
        <div v-if="planned.length" class="d-flex flex-column gap-2">
          <div v-for="log in planned" :key="log.id" class="card bg-dark border-0 p-3">
            <div class="d-flex gap-3 align-items-start">
              <div class="poster-thumb bg-secondary rounded d-flex align-items-center justify-content-center flex-shrink-0">
                <IconPhoto :size="16" class="text-secondary" />
              </div>
              <div class="flex-grow-1 min-w-0">
                <div class="fw-medium small mb-1">{{ log.performance_str || `公演 #${log.performance}` }}</div>
                <span class="badge bg-warning bg-opacity-25 text-warning tiny">これから観る</span>
                <div v-if="log.memo" class="tiny text-secondary mt-2 text-truncate-2">{{ log.memo }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">これから観る作品はまだありません</p>
          <div class="d-flex flex-column gap-2 align-items-center">
            <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
            <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
          </div>
        </div>
      </section>

      <!-- Tab: 観た -->
      <section v-if="activeTab === 'watched'">
        <h3 class="small fw-semibold text-secondary mb-3">
          <IconEye :size="14" class="me-1" />観た作品
        </h3>
        <div v-if="watched.length" class="d-flex flex-column gap-2">
          <div v-for="log in watched" :key="log.id" class="card bg-dark border-0 p-3">
            <div class="d-flex gap-3 align-items-start">
              <div class="poster-thumb bg-secondary rounded d-flex align-items-center justify-content-center flex-shrink-0">
                <IconPhoto :size="16" class="text-secondary" />
              </div>
              <div class="flex-grow-1 min-w-0">
                <div class="fw-medium small mb-1">{{ log.performance_str || `公演 #${log.performance}` }}</div>
                <div class="d-flex align-items-center gap-2">
                  <span class="badge bg-success bg-opacity-25 text-success tiny">観た</span>
                  <span v-if="log.watched_on" class="tiny text-secondary">{{ formatDate(log.watched_on) }}</span>
                </div>
                <div v-if="log.memo" class="tiny text-secondary mt-2 text-truncate-2">{{ log.memo }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">観た作品はまだありません</p>
          <div class="d-flex flex-column gap-2 align-items-center">
            <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
            <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
          </div>
        </div>
      </section>

      <!-- Tab: 感想 -->
      <section v-if="activeTab === 'reviews'">
        <h3 class="small fw-semibold text-secondary mb-3">
          <IconMessage :size="14" class="me-1" />感想
        </h3>
        <div v-if="myReviews.length" class="d-flex flex-column gap-2">
          <div v-for="r in myReviews" :key="r.id" class="card bg-dark border-0 p-3">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div class="fw-medium small">{{ r.performance_str || r.title || '感想' }}</div>
              <span v-if="r.is_spoiler" class="badge bg-danger bg-opacity-25 text-danger tiny">ネタバレ</span>
            </div>
            <div v-if="r.rating_overall" class="mb-2">
              <span class="small" style="color: #f59e0b;">
                <IconStar :size="13" v-for="n in r.rating_overall" :key="n" />
              </span>
            </div>
            <p class="small text-light mb-2 lh-base review-body">{{ r.body }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <span class="tiny text-secondary">
                <IconHeart :size="12" /> {{ r.like_count || 0 }}
              </span>
              <span class="tiny text-secondary">{{ formatDate(r.created_at?.slice(0, 10)) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">まだ感想はありません</p>
          <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
        </div>
      </section>

      <!-- Tab: ポスター -->
      <section v-if="activeTab === 'posters'">
        <h3 class="small fw-semibold text-secondary mb-3">
          <IconPhoto :size="14" class="me-1" />投稿したポスター
        </h3>
        <div v-if="myPosters.length" class="row g-2">
          <div v-for="p in myPosters" :key="p.id" class="col-6">
            <div class="card bg-dark border-0 overflow-hidden">
              <img :src="p.image" class="card-img-top" :alt="p.caption" style="aspect-ratio: 3/4; object-fit: cover;">
              <div class="card-body p-2">
                <div class="tiny fw-medium text-truncate">{{ p.work_title }}</div>
                <div v-if="p.caption" class="tiny text-secondary text-truncate">{{ p.caption }}</div>
                <span v-if="p.is_selected" class="badge bg-info bg-opacity-25 text-info tiny mt-1">採用中</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">まだポスター投稿はありません</p>
          <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探して投稿する</RouterLink>
        </div>
      </section>

      <!-- Logout -->
      <div class="mt-5 pt-3 border-top border-secondary">
        <button class="btn btn-dark w-100 text-secondary" @click="logout">ログアウト</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.poster-thumb {
  width: 48px;
  height: 64px;
  background: #27272a !important;
}
.tiny {
  font-size: 0.7rem;
}
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.review-body {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
