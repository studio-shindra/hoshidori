<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import {
  IconArrowLeft,
  IconCamera,
  IconHeart,
  IconHeartFilled,
  IconMask,
  IconStar,
  IconTicket,
  IconMapPin,
  IconPlus,
} from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const work = ref(null)
const performances = ref([])
const reviews = ref([])
const nearbyShops = ref([])
const loading = ref(true)

// review form
const showReviewForm = ref(false)
const reviewPerf = ref('')
const reviewBody = ref('')
const reviewRating = ref('')
const reviewSpoiler = ref(false)
const reviewError = ref('')
const reviewLoading = ref(false)

// log form
const showLogForm = ref(false)
const logPerf = ref('')
const logStatus = ref('planned')
const logWatchedOn = ref('')
const logMemo = ref('')
const logError = ref('')
const logLoading = ref(false)
const logSuccess = ref('')

const perfIds = computed(() => performances.value.map((p) => p.id))
const workReviews = computed(() =>
  reviews.value.filter((r) => perfIds.value.includes(r.performance)),
)

const theaterSlug = computed(() => {
  const p = performances.value[0]
  return p ? p.theater_slug : null
})
const theaterName = computed(() => {
  const p = performances.value[0]
  return p ? p.theater_name : ''
})
const companyName = computed(() => {
  const p = performances.value[0]
  return p ? p.company_name : ''
})
const dateRange = computed(() => {
  if (!performances.value.length) return ''
  const dates = performances.value.map((p) => p.start_date).filter(Boolean)
  if (!dates.length) return ''
  return dates[0]
})

const hasPoster = computed(() => !!work.value?.selected_poster_image_url)
const posterUrl = computed(() => work.value?.selected_poster_image_url)
const posterCredit = computed(() => work.value?.selected_poster_user_display_name)

async function fetchShops() {
  if (!theaterSlug.value) return
  try {
    const data = await api.get(`/api/theaters/${theaterSlug.value}/shops/`)
    nearbyShops.value = (data.results || data).slice(0, 3)
  } catch {
    /* empty */
  }
}

const sortedShops = computed(() =>
  [...nearbyShops.value].sort((a, b) => (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0)),
)

onMounted(async () => {
  try {
    const slug = route.params.slug
    work.value = await api.get(`/api/works/${slug}/`)

    const [perfData, revData] = await Promise.all([
      api.get('/api/performances/'),
      api.get('/api/reviews/'),
    ])
    const allPerfs = perfData.results || perfData
    performances.value = allPerfs.filter(
      (p) => p.work === work.value.id || p.work_slug === slug,
    )
    reviews.value = revData.results || revData

    await fetchShops()
  } finally {
    loading.value = false
  }
})

function perfLabel(p) {
  const parts = []
  if (p.theater_name) parts.push(p.theater_name)
  if (p.start_date) parts.push(p.start_date)
  if (p.company_name) parts.push(p.company_name)
  return parts.length ? parts.join(' / ') : `公演 #${p.id}`
}

function openLogForm(status) {
  showLogForm.value = true
  showReviewForm.value = false
  logStatus.value = status
  logPerf.value = performances.value.length === 1 ? performances.value[0].id : ''
  logError.value = ''
  logSuccess.value = ''
}

async function submitLog() {
  logError.value = ''
  logSuccess.value = ''
  logLoading.value = true
  try {
    const body = {
      performance: Number(logPerf.value),
      status: logStatus.value,
      memo: logMemo.value,
    }
    if (logStatus.value === 'watched' && logWatchedOn.value) {
      body.watched_on = logWatchedOn.value
    }
    await api.post('/api/viewing-logs/', body)
    logSuccess.value = '保存しました'
    logMemo.value = ''
    logWatchedOn.value = ''
  } catch (e) {
    logError.value = e.data ? Object.values(e.data).flat().join(' ') : '保存に失敗しました'
  } finally {
    logLoading.value = false
  }
}

function openReviewForm() {
  showReviewForm.value = true
  showLogForm.value = false
  reviewPerf.value = performances.value.length === 1 ? performances.value[0].id : ''
  reviewError.value = ''
}

async function submitReview() {
  reviewError.value = ''
  reviewLoading.value = true
  try {
    const body = {
      performance: Number(reviewPerf.value),
      body: reviewBody.value,
      is_spoiler: reviewSpoiler.value,
    }
    if (reviewRating.value) body.rating_overall = Number(reviewRating.value)
    const newReview = await api.post('/api/reviews/', body)
    reviews.value.unshift(newReview)
    showReviewForm.value = false
    reviewBody.value = ''
    reviewRating.value = ''
    reviewSpoiler.value = false
  } catch (e) {
    reviewError.value = e.data ? Object.values(e.data).flat().join(' ') : '投稿に失敗しました'
  } finally {
    reviewLoading.value = false
  }
}

async function toggleLike(review) {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: route.fullPath } })
    return
  }
  try {
    if (review.is_liked) {
      await api.delete(`/api/reviews/${review.id}/like/`)
      review.is_liked = false
      review.like_count--
    } else {
      await api.post(`/api/reviews/${review.id}/like/`)
      review.is_liked = true
      review.like_count++
    }
  } catch {
    /* empty */
  }
}
</script>

<template>
  <div>
    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="work">
      <!-- Hero image area -->
      <div class="position-relative">
        <template v-if="hasPoster">
          <div class="hero">
            <img :src="posterUrl" class="w-100 h-100 object-fit-cover" />
          </div>
        </template>
        <template v-else>
          <div class="hero poster-empty d-flex flex-column align-items-center justify-content-center gap-2">
            <IconMask :size="48" class="text-secondary" />
            <span class="text-secondary small">ポスター画像募集中</span>
            <RouterLink
              :to="`/works/${route.params.slug}/poster`"
              class="btn btn-sm btn-outline-secondary mt-1"
            >
              <IconCamera :size="14" class="me-1" />最初の1枚を投稿
            </RouterLink>
          </div>
        </template>
        <button
          class="btn btn-dark btn-sm position-absolute top-0 start-0 m-3 rounded-circle back-btn"
          @click="router.back()"
        >
          <IconArrowLeft :size="16" />
        </button>
        <div class="hero-fade"></div>
      </div>

      <!-- Work info -->
      <div class="px-3 position-relative" style="margin-top: -2.5rem; z-index: 2">
        <h2 class="fs-5 fw-bold mb-1">{{ work.title || work.name }}</h2>
        <div class="small text-secondary" v-if="companyName">{{ companyName }}</div>
        <div class="small text-secondary">
          <span v-if="theaterName">{{ theaterName }}</span>
          <span v-if="dateRange"> · {{ dateRange }}</span>
        </div>

        <div class="tiny text-secondary mt-2">
          <template v-if="hasPoster">
            Top image by @{{ posterCredit }} ·
          </template>
          <template v-else>ポスター画像募集中 · </template>
          <RouterLink :to="`/works/${route.params.slug}/poster`" class="text-secondary">ポスターを投稿</RouterLink>
        </div>

        <!-- Action buttons -->
        <template v-if="auth.isAuthenticated">
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-dark flex-fill color-amber fw-medium" @click="openLogForm('planned')">
              <IconTicket :size="16" class="me-1" />これから観る
            </button>
            <button class="btn btn-dark flex-fill color-green fw-medium" @click="openLogForm('watched')">
              <IconStar :size="16" class="me-1" />観た
            </button>
            <button class="btn btn-primary-rose flex-fill fw-medium" @click="openReviewForm()">感想を書く</button>
          </div>

          <div class="d-flex gap-2 mt-2">
            <RouterLink to="/logs/new" class="btn btn-outline-secondary btn-sm flex-fill">記録ページへ</RouterLink>
            <RouterLink :to="`/works/${route.params.slug}/poster`" class="btn btn-outline-secondary btn-sm flex-fill">
              <IconCamera :size="14" class="me-1" />ポスター投稿
            </RouterLink>
          </div>

          <!-- 公演追加導線 -->
          <div class="mt-2">
            <RouterLink to="/performances/new" class="btn btn-outline-secondary btn-sm w-100">
              <IconPlus :size="14" class="me-1" />公演を追加
            </RouterLink>
          </div>
        </template>
        <div v-else class="mt-3">
          <RouterLink :to="{ name: 'login', query: { next: route.fullPath } }" class="text-secondary small">
            ログインして記録・感想を投稿 →
          </RouterLink>
        </div>
      </div>

      <!-- Log form (inline) -->
      <section v-if="showLogForm" class="mx-3 mt-3 card bg-dark border-secondary p-3">
        <h3 class="small fw-semibold mb-3">{{ logStatus === 'planned' ? 'これから観るを登録' : '観たを記録' }}</h3>
        <form @submit.prevent="submitLog" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label tiny text-secondary">公演</label>
            <select v-model="logPerf" required class="form-select bg-dark border-secondary text-light form-select-sm">
              <option value="" disabled>選択してください</option>
              <option v-for="p in performances" :key="p.id" :value="p.id">{{ perfLabel(p) }}</option>
            </select>
          </div>
          <div v-if="logStatus === 'watched'">
            <label class="form-label tiny text-secondary">観劇日</label>
            <input v-model="logWatchedOn" type="date" class="form-control bg-dark border-secondary text-light form-control-sm" />
          </div>
          <div>
            <label class="form-label tiny text-secondary">メモ</label>
            <textarea v-model="logMemo" rows="2" placeholder="メモ（任意）" class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
          </div>
          <p v-if="logError" class="small text-danger mb-0">{{ logError }}</p>
          <p v-if="logSuccess" class="small color-green mb-0">{{ logSuccess }}</p>
          <div class="d-flex gap-2">
            <button type="submit" :disabled="logLoading" class="btn btn-primary-rose btn-sm flex-fill">
              {{ logLoading ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn btn-dark btn-sm flex-fill text-secondary" @click="showLogForm = false">キャンセル</button>
          </div>
        </form>
      </section>

      <!-- Review form (inline) -->
      <section v-if="showReviewForm" class="mx-3 mt-3 card bg-dark border-secondary p-3">
        <h3 class="small fw-semibold mb-3">感想を書く</h3>
        <form @submit.prevent="submitReview" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label tiny text-secondary">公演</label>
            <select v-model="reviewPerf" required class="form-select bg-dark border-secondary text-light form-select-sm">
              <option value="" disabled>選択してください</option>
              <option v-for="p in performances" :key="p.id" :value="p.id">{{ perfLabel(p) }}</option>
            </select>
          </div>
          <div>
            <label class="form-label tiny text-secondary">感想</label>
            <textarea v-model="reviewBody" rows="4" placeholder="感想を書く" required class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
          </div>
          <div>
            <label class="form-label tiny text-secondary">評価（1〜5、任意）</label>
            <input v-model="reviewRating" type="number" min="1" max="5" placeholder="任意" class="form-control bg-dark border-secondary text-light form-control-sm" />
          </div>
          <div class="form-check">
            <input v-model="reviewSpoiler" type="checkbox" class="form-check-input" id="spoilerCheck" />
            <label for="spoilerCheck" class="form-check-label small text-secondary">ネタバレを含む</label>
          </div>
          <p v-if="reviewError" class="small text-danger mb-0">{{ reviewError }}</p>
          <div class="d-flex gap-2">
            <button type="submit" :disabled="reviewLoading" class="btn btn-primary-rose btn-sm flex-fill">
              {{ reviewLoading ? '投稿中...' : '投稿' }}
            </button>
            <button type="button" class="btn btn-dark btn-sm flex-fill text-secondary" @click="showReviewForm = false">キャンセル</button>
          </div>
        </form>
      </section>

      <!-- Reviews section -->
      <section class="mt-4 px-3">
        <h3 class="small fw-semibold text-secondary mb-3">みんなの感想</h3>
        <div v-if="workReviews.length" class="d-flex flex-column gap-3">
          <div v-for="r in workReviews" :key="r.id" class="card bg-dark border-0 p-3">
            <div class="d-flex align-items-center gap-2 mb-2">
              <div class="avatar-sm">{{ (r.user_display_name || r.username || '匿')[0].toUpperCase() }}</div>
              <span class="small fw-medium">{{ r.user_display_name || r.username || '匿名' }}</span>
              <span v-if="r.rating_overall" class="ms-auto small color-amber">
                <IconStar :size="14" /> {{ r.rating_overall }}
              </span>
            </div>
            <p v-if="r.is_spoiler" class="tiny color-rose mb-1">ネタバレあり</p>
            <p class="small text-light mb-2 lh-base">{{ r.body }}</p>
            <button
              class="btn btn-link btn-sm p-0 text-decoration-none small"
              :class="r.is_liked ? 'color-rose' : 'text-secondary'"
              @click="toggleLike(r)"
            >
              <component :is="r.is_liked ? IconHeartFilled : IconHeart" :size="14" />
              {{ r.like_count || 0 }}
            </button>
          </div>
        </div>
        <p v-else class="text-secondary small">まだ感想がありません</p>
      </section>

      <!-- Nearby shops -->
      <section v-if="sortedShops.length" class="mt-4 px-3 mb-5">
        <h3 class="small fw-semibold text-secondary mb-3">
          <IconMapPin :size="14" class="me-1" />
          {{ theaterName }} の近くの店
        </h3>
        <div class="d-flex flex-column gap-3">
          <RouterLink
            v-for="s in sortedShops"
            :key="s.id"
            :to="`/shops/${s.slug}`"
            class="card border-0 p-0 overflow-hidden text-decoration-none"
            :class="s.is_featured ? 'shop-featured' : 'bg-dark'"
          >
            <div class="position-relative">
              <div class="shop-img" :class="s.is_featured ? 'shop-img-featured' : ''"></div>
              <span v-if="s.is_featured" class="badge badge-featured position-absolute top-0 start-0 m-2">おすすめ</span>
            </div>
            <div class="p-3">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-medium small text-light">{{ s.name }}</div>
                  <div class="tiny text-secondary">{{ s.category || '' }}</div>
                  <div class="tiny text-secondary mt-1">{{ s.description || '' }}</div>
                </div>
                <span v-if="s.benefit_text" class="btn btn-sm btn-coupon flex-shrink-0 ms-2">{{ s.benefit_text }}</span>
              </div>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.hero {
  width: 100%;
  aspect-ratio: 4 / 5;
  overflow: hidden;
}
.hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6rem;
  background: linear-gradient(transparent, #0a0a0b);
}
.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
.shop-img {
  width: 100%;
  height: 100px;
  background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
}
.shop-img-featured {
  height: 120px;
  background: linear-gradient(135deg, #44403c 0%, #57534e 50%, #44403c 100%);
}
.shop-featured {
  background: #1c1917;
  border: 1px solid rgba(245, 158, 11, 0.25);
}
</style>
