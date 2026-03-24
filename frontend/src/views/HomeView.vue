<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_THUMB } from '@/lib/cloudinary'
import { IconMask, IconTicket, IconStar, IconCoffee, IconMessage, IconHeart } from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'
import WorkCard from '@/components/WorkCard.vue'
import LogListItem from '@/components/LogListItem.vue'
import ShopCard from '@/components/ShopCard.vue'
import HomeSkeleton from '@/components/HomeSkeleton.vue'

const auth = useAuthStore()
const loading = ref(true)
const plannedLogs = ref([])
const watchedLogs = ref([])
const featuredShops = ref([])
const wantToGoShops = ref([])
const latestReviews = ref([])

const plannedCount = computed(() => plannedLogs.value.length)
const watchedCount = computed(() => watchedLogs.value.length)
const watchedVisible = computed(() => watchedLogs.value.slice(0, 12))

async function fetchData() {
  loading.value = true
  try {
    const [pData, wData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
    ])
    plannedLogs.value = pData.results || pData
    watchedLogs.value = wData.results || wData
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
}

async function fetchFeaturedShops() {
  try {
    const data = await api.get('/api/shops/featured/')
    featuredShops.value = data.results || data
  } catch {
    /* empty */
  }
}

async function fetchWantToGoShops() {
  try {
    const data = await api.get('/api/shops/want-to-go/')
    wantToGoShops.value = data.results || data
  } catch {
    /* empty */
  }
}

function onWantToGoChanged() {
  fetchWantToGoShops()
}

async function fetchLatestReviews() {
  try {
    const data = await api.get('/api/reviews/latest/')
    latestReviews.value = data.results || data
  } catch {
    /* empty */
  }
}

onMounted(async () => {
  const publicFetches = [fetchFeaturedShops(), fetchLatestReviews()]
  if (auth.isAuthenticated) {
    await Promise.all([...publicFetches, fetchData(), fetchWantToGoShops()])
  } else {
    loading.value = false
    await Promise.all(publicFetches)
  }
})
</script>

<template>
  <div>


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
      <HomeSkeleton v-if="loading" />
      <template v-else>

        <!-- これから観る -->
        <section class="mb-4">
          <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
            <IconTicket :size="20" />
            観る
            <span v-if="plannedCount" class="count-circle">{{ plannedCount }}</span>
          </h2>
          <div v-if="plannedLogs.length" class="d-flex gap-2 overflow-auto scroll-hide">
            <WorkCard
              v-for="log in plannedLogs"
              :key="log.id"
              :poster-url="log.poster_url"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :theater-name="log.theater_name"
            />
          </div>
          <div v-else class="card bg-dark border-0 p-4 text-center">
            <p class="text-secondary small mb-2">気になる作品をクリップしよう</p>
            <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
          </div>
        </section>

        <!-- 最近観た作品 -->
        <section class="mb-4">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h2 class="d-flex align-items-center gap-2 fw-bold fs-2 mb-0">
              <IconStar :size="20" />
              観た
              <span v-if="watchedCount" class="count-circle">{{ watchedCount }}</span>
            </h2>
            <RouterLink v-if="watchedCount > 12" to="/mypage" class="text-secondary small text-decoration-none">すべて見る →</RouterLink>
          </div>
          <div v-if="watchedLogs.length" class="watched-grid overflow-auto scroll-hide">
            <LogListItem
              v-for="log in watchedVisible"
              :key="log.id"
              :poster-url="log.poster_url"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :watched-on="log.watched_on"
              :watched-time="log.watched_time"
              :theater-name="log.theater_name"
              :theater-area="log.theater_area"
              :memo="log.memo"
              :rating="log.rating"
              :images="log.images"
              compact
            />
          </div>
          <div v-else class="card bg-dark border-0 p-4 text-center">
            <p class="text-secondary small mb-2">観劇したら記録を残そう</p>
            <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
          </div>
        </section>
      </template>
    </template>

    <!-- 行きたい店 (ログイン中のみ) -->
    <section v-if="auth.isAuthenticated" class="mb-4">
      <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
        <IconHeart :size="20" />
        観劇後・観劇前に
      </h2>
      <div v-if="wantToGoShops.length" class="d-flex gap-2 overflow-auto scroll-hide align-items-stretch">
        <div v-for="shop in wantToGoShops" :key="shop.id" class="flex-shrink-0 want-to-go-card-wrap d-flex">
          <ShopCard :shop="shop" @want-to-go-changed="onWantToGoChanged" />
        </div>
      </div>
      <div v-else class="card bg-dark border-0 p-4 text-center">
        <p class="text-secondary small mb-2">気になるお店をハートで保存しよう</p>
        <RouterLink to="/shops" class="btn btn-sm btn-outline-secondary">お店を探す</RouterLink>
      </div>
    </section>

    <!-- おすすめの店 (ログイン不問) -->
    <section v-if="featuredShops.length" class="mb-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h2 class="d-flex align-items-center gap-2 fw-bold fs-2 mb-0">
          <IconCoffee :size="20" />
          おすすめの店
        </h2>
        <RouterLink to="/shops" class="text-secondary small text-decoration-none">すべて見る →</RouterLink>
      </div>
      <div class="d-flex gap-2 overflow-auto scroll-hide align-items-stretch">
        <div v-for="shop in featuredShops" :key="shop.id" class="flex-shrink-0 want-to-go-card-wrap d-flex">
          <ShopCard :shop="shop" @want-to-go-changed="onWantToGoChanged" />
        </div>
      </div>
    </section>
    <section v-else-if="!loading" class="mb-4">
      <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
        <IconCoffee :size="20" />
        おすすめの店
      </h2>
      <p class="text-secondary small">まだおすすめの店はありません</p>
    </section>

    <!-- 最新のコメント (ログイン不問) -->
    <section v-if="latestReviews.length" class="mb-4">
      <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
        <IconMessage :size="20" />
        最新のコメント
      </h2>
      <div class="d-flex gap-3 overflow-auto scroll-hide">
        <RouterLink
          v-for="r in latestReviews"
          :key="r.id"
          :to="`/works/${r.work_slug}`"
          class="text-decoration-none flex-shrink-0 review-card"
        >
          <div class="card bg-dark border-0 p-2 h-100">
            <div class="d-flex gap-2">
              <div class="review-poster-wrap flex-shrink-0">
                <img v-if="r.poster_url" :src="cloudinaryUrl(r.poster_url, IMG_THUMB)" :alt="r.work_title" class="review-poster" loading="lazy" />
                <div v-else class="review-poster review-poster-empty"></div>
              </div>
              <div class="min-w-0 flex-grow-1">
                <div class="fw-bold text-white text-truncate">{{ r.work_title }}</div>
                <div class="d-flex align-items-center gap-1 mt-1">
                  <UserAvatar :src="r.user_avatar_url" :name="r.user_display_name" :size="18" />
                  <span class="small text-secondary text-truncate">{{ r.user_display_name }}</span>
                  <span v-if="r.rating_overall" class="review-rating-badge ms-auto">
                    {{ r.rating_overall === 5 ? '最高' : r.rating_overall === 4 ? '良かった' : '観た' }}
                  </span>
                </div>
                <p class="small text-white-50 mt-1 mb-0 review-body">{{ r.body }}</p>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.want-to-go-card-wrap {
  width: 200px;
}
.count-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #fff;
  color: #000;
  font-size: 0.85rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.watched-grid {
  display: grid;
  grid-template-rows: repeat(3, auto);
  grid-auto-flow: column;
  grid-auto-columns: min(calc(100vw - 40px), 400px);
  gap: 8px;
}
.watched-grid > :deep(*) {
  overflow: hidden;
  min-width: 0;
}
.watched-grid :deep(.card-sm) {
  width: 72px;
  flex-shrink: 0;
}
.review-card {
  width: min(calc(100vw - 40px), 320px);
}
.review-poster-wrap {
  width: 56px;
}
.review-poster {
  width: 56px;
  height: 80px;
  border-radius: 6px;
  object-fit: cover;
}
.review-poster-empty {
  width: 56px;
  height: 80px;
  border-radius: 6px;
  background: linear-gradient(135deg, #27272a, #3f3f46);
}
.review-body {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}
.review-rating-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
