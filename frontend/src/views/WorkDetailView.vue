<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import Multiselect from '@vueform/multiselect'
import {
  IconArrowLeft,
  IconCamera,
  IconHeart,
  IconHeartFilled,
  IconStar,
  IconTicket,
  IconMapPin,
  IconPlus,
  IconFlag,
  IconX,
} from '@tabler/icons-vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
const MAX_FILE_SIZE = 10 * 1024 * 1024
const MAX_IMAGES = 4
import ShopCard from '@/components/ShopCard.vue'
import PosterImage from '@/components/PosterImage.vue'
import { ratingLabel, ratingIcon } from '@/lib/rating'
import { IconThumbUp, IconHeartHandshake, IconSparkles } from '@tabler/icons-vue'
import RatingButtons from '@/components/RatingButtons.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import AppLoader from '@/components/AppLoader.vue'

const ratingIcons = { IconThumbUp, IconHeartHandshake, IconSparkles }

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const work = ref(null)
const performances = ref([])
const reviews = ref([])
const workPosters = ref([])
const nearbyShops = ref([])
const loading = ref(true)
const detailTab = ref('memo')

// log form
const showLogForm = ref(false)
const logPerf = ref('')
const logStatus = ref('planned')
const logWatchedOn = ref('')
const logMemo = ref('')
const logRating = ref('')
const logSpoiler = ref(false)
const logError = ref('')
const logLoading = ref(false)
const logSuccess = ref('')
const logImages = ref([])
const logImageInput = ref(null)

function onLogImageSelect(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    if (logImages.value.length >= MAX_IMAGES) break
    if (!file.type.startsWith('image/')) continue
    if (file.size > MAX_FILE_SIZE) continue
    logImages.value.push({ file, preview: URL.createObjectURL(file) })
  }
  e.target.value = ''
}

function removeLogImage(index) {
  URL.revokeObjectURL(logImages.value[index].preview)
  logImages.value.splice(index, 1)
}

async function uploadLogImages(logId) {
  for (let i = 0; i < logImages.value.length; i++) {
    const { file } = logImages.value[i]
    const fd = new FormData()
    fd.append('file', file)
    fd.append('upload_preset', UPLOAD_PRESET)
    const cloudRes = await fetch(
      `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
      { method: 'POST', body: fd }
    )
    if (!cloudRes.ok) continue
    const d = await cloudRes.json()
    await api.post(`/api/viewing-logs/${logId}/images/`, {
      image_url: d.secure_url,
      image_public_id: d.public_id,
      image_width: d.width,
      image_height: d.height,
      image_format: d.format,
      order: i,
    })
  }
}

const workReviews = computed(() => reviews.value)

const perfOptions = computed(() =>
  performances.value.map((p) => ({ value: p.id, label: perfLabel(p) })),
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

const averageRating = computed(() => {
  const rated = workReviews.value.filter((r) => r.rating_overall)
  if (!rated.length) return null
  const sum = rated.reduce((a, r) => a + r.rating_overall, 0)
  return (sum / rated.length).toFixed(1)
})
const reviewCount = computed(() => workReviews.value.length)

const posterUrl = computed(() => work.value?.selected_poster_image_url)
const posterCredit = computed(() => work.value?.selected_poster_user_display_name)
const posterCreditAvatar = computed(() => work.value?.selected_poster_user_avatar_url)

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

    const workId = work.value.id
    const [perfData, revData, posterData] = await Promise.all([
      api.get(`/api/performances/?work=${workId}`),
      api.get(`/api/reviews/?work=${workId}`),
      api.get(`/api/works/${slug}/posters/`),
    ])
    performances.value = perfData.results || perfData
    reviews.value = revData.results || revData
    workPosters.value = Array.isArray(posterData) ? posterData : posterData.results || []

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
    const log = await api.post('/api/viewing-logs/', body)
    // 画像アップロード
    if (logImages.value.length && logStatus.value === 'watched') {
      await uploadLogImages(log.id)
    }
    // 感想があればレビューも同時作成
    if (logMemo.value.trim()) {
      const reviewBody = {
        performance: Number(logPerf.value),
        body: logMemo.value,
        is_spoiler: logSpoiler.value,
      }
      if (logRating.value) reviewBody.rating_overall = Number(logRating.value)
      const newReview = await api.post('/api/reviews/', reviewBody)
      reviews.value.unshift(newReview)
    }
    logSuccess.value = '保存しました'
    logMemo.value = ''
    logWatchedOn.value = ''
    logRating.value = ''
    logSpoiler.value = false
    logImages.value = []
  } catch (e) {
    logError.value = e.data ? Object.values(e.data).flat().join(' ') : '保存に失敗しました'
  } finally {
    logLoading.value = false
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
    <AppLoader v-if="loading" />
    <template v-else-if="work">
      <!-- Hero image area -->
      <div class="position-relative">
        <div class="hero">
          <PosterImage :src="posterUrl" :alt="work.title || work.name" :work-slug="route.params.slug" :credit="posterCredit" :credit-avatar="posterCreditAvatar" size="lg" />
          <div v-if="!posterUrl" class="position-absolute bottom-0 start-0 end-0 text-center pb-4" style="z-index:1">
            <RouterLink :to="`/works/${route.params.slug}/poster`" class="btn btn-sm btn-outline-secondary">
              <IconCamera :size="14" class="me-1" />最初の1枚を投稿
            </RouterLink>
          </div>
        </div>
        <div class="hero-fade"></div>
      </div>

      <!-- Work info -->
      <div class="position-relative" style="margin-top: -1rem; z-index: 2">
        <h2 class="fs-5 fw-bold mb-1">{{ work.title || work.name }}</h2>
        <div class="small" v-if="companyName">{{ companyName }}</div>
        <div class="small">
          <span v-if="theaterName">{{ theaterName }}</span>
          <span v-if="dateRange"> · {{ dateRange }}</span>
        </div>

        <!-- Action buttons -->
        <template v-if="auth.isAuthenticated">
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-light flex-fill color-white d-flex align-items-center justify-content-center" @click="openLogForm('planned')">
              <IconTicket :size="16" class="me-1" />観る
            </button>
            <button class="btn flex-fill btn-primary-rose d-flex align-items-center justify-content-center" @click="openLogForm('watched')">
              <IconStar :size="16" class="me-1" />観た
            </button>
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
        <h3 class="small fw-semibold mb-3">{{ logStatus === 'planned' ? '観るを登録' : '観たを記録' }}</h3>
        <form @submit.prevent="submitLog" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label tiny text-secondary">公演</label>
            <Multiselect
              v-model="logPerf"
              :options="perfOptions"
              :searchable="true"
              placeholder="公演を検索..."
              no-results-text="該当する公演がありません"
              no-options-text="公演データがありません"
              class="multiselect-dark"
            >
              <template #noresults>
                <div class="py-2 text-center">
                  <span class="small text-secondary">該当する公演がありません</span>
                  <RouterLink to="/performances/new" class="d-block small mt-1 color-rose">公演を新しく追加する →</RouterLink>
                </div>
              </template>
            </Multiselect>
          </div>
          <div v-if="logStatus === 'watched'">
            <label class="form-label tiny text-secondary">観劇日</label>
            <input v-model="logWatchedOn" type="date" class="form-control bg-dark border-secondary text-light form-control-sm" />
          </div>
          <template v-if="logStatus === 'watched'">
            <div>
              <label class="form-label tiny text-secondary">写真（最大{{ MAX_IMAGES }}枚）</label>
              <input ref="logImageInput" type="file" accept="image/*" multiple class="d-none" @change="onLogImageSelect" />
              <div class="d-flex gap-2 flex-wrap">
                <div v-for="(img, i) in logImages" :key="i" class="img-thumb">
                  <img :src="img.preview" class="w-100 h-100 object-fit-cover rounded" />
                  <button class="img-thumb-remove" @click="removeLogImage(i)"><IconX :size="12" /></button>
                </div>
                <button v-if="logImages.length < MAX_IMAGES" class="img-thumb img-thumb-add" @click="logImageInput?.click()">
                  <IconCamera :size="20" class="text-secondary" />
                </button>
              </div>
            </div>
            <div>
              <label class="form-label tiny text-secondary">感想・メモ</label>
              <textarea v-model="logMemo" rows="4" placeholder="感想やメモ（任意）" class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
            </div>
          </template>
          <template v-if="logStatus === 'watched'">
            <div>
              <label class="form-label tiny text-secondary">評価（任意）</label>
              <RatingButtons v-model="logRating" />
            </div>
            <div class="form-check">
              <input v-model="logSpoiler" type="checkbox" class="form-check-input" id="spoilerCheck" />
              <label for="spoilerCheck" class="form-check-label small text-secondary">ネタバレを含む</label>
            </div>
          </template>
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

      <!-- Memo / Poster tabs -->
      <section class="mt-4">
        <div class="d-flex border-bottom border-secondary mb-3">
          <button class="detail-tab flex-fill" :class="{ active: detailTab === 'memo' }" @click="detailTab = 'memo'">
            観劇メモ
            <span v-if="reviewCount" class="tab-count">{{ reviewCount }}</span>
          </button>
          <button class="detail-tab flex-fill" :class="{ active: detailTab === 'poster' }" @click="detailTab = 'poster'">
            ポスター
            <span v-if="workPosters.length" class="tab-count">{{ workPosters.length }}</span>
          </button>
        </div>

        <div class="detail-tab-content scroll-hide">
          <!-- メモ -->
          <template v-if="detailTab === 'memo'">
            <div v-if="averageRating" class="df-center gap-2 mb-3 ">
              <div class="df-center gap-2">
                <span class="badge bg-amber fw-bold">レビュー平均</span>
                <span class="fw-bold fs-4">{{ averageRating }}</span>
              </div>
            </div>
            <div v-if="workReviews.length" class="d-flex flex-column gap-3">
              <div v-for="r in workReviews" :key="r.id" class="card bg-dark border-0 p-3">
                <div class="d-flex align-items-center gap-2 mb-2">
                  <UserAvatar :src="r.user_avatar_url" :name="r.user_display_name" :size="28" />
                  <span class="small fw-medium">{{ r.user_display_name }}</span>
                  <span v-if="r.rating_overall" class="ms-auto d-flex align-items-center gap-1 small bg-amber text-white px-2 rounded fw-bold">
                    <component :is="ratingIcons[ratingIcon(r.rating_overall)]" :size="14" />
                    {{ ratingLabel(r.rating_overall) }}
                  </span>
                </div>
                <p v-if="r.is_spoiler" class="tiny color-rose mb-1">ネタバレあり</p>
                <p class="small text-light lh-base py-2 my-2 border-secondary border-top">{{ r.body }}</p>
                <div class="text-start">
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
            </div>
            <div v-else class="text-center py-4">
              <p class="text-secondary small mb-2">まだ感想はありません</p>
              <button v-if="auth.isAuthenticated" class="btn btn-sm btn-outline-secondary" @click="openLogForm('watched')">最初の観劇メモを残す</button>
            </div>
          </template>

          <!-- ポスター -->
          <template v-if="detailTab === 'poster'">
            <div v-if="workPosters.length" class="grid-wrapper">
              <div v-for="p in workPosters" :key="p.id" class="position-relative">
                <PosterImage :src="p.image_url || p.image" :credit="p.user_display_name" :credit-avatar="p.user_avatar_url" size="md" />
                <a
                  :href="`mailto:info@studio-shindra.com?subject=${encodeURIComponent('[HOSHIDORI] 画像通報')}&body=${encodeURIComponent('通報対象: ' + (work.title || '') + ' のポスター画像\n画像ID: ' + p.id + '\n\n通報理由: ')}`"
                  class="poster-report-btn"
                  title="この画像を通報"
                >
                  <IconFlag :size="12" />
                </a>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <p class="text-secondary small mb-2">まだポスターはありません</p>
              <RouterLink v-if="auth.isAuthenticated" :to="`/works/${route.params.slug}/poster`" class="btn btn-sm btn-outline-secondary">
                <IconCamera :size="14" class="me-1" />ポスターを投稿する
              </RouterLink>
            </div>
          </template>
        </div>
      </section>

      <!-- Nearby shops -->
      <section v-if="sortedShops.length" class="mt-4 mb-5">
        <div class="bg-white df-center w-100 text-black p-2 mb-3 mt-5 rounded fw-bold">
          <IconMapPin :size="14" class="me-1" />{{ theaterName }} の近くの店
        </div>
        <div class="d-flex flex-column gap-3">
          <ShopCard v-for="s in sortedShops" :key="s.id" :shop="s" />
        </div>
      </section>
    </template>
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
<style scoped>

.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}

.detail-tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #a1a1aa;
  padding: 0.6rem 0;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  &.active {
    color: #fff;
    border-bottom-color: #fff;
  }
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: #000;
  font-size: 0.6rem;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  padding: 0 4px;
  margin-left: 4px;
}

.detail-tab-content {
  max-height: 60vh;
  overflow-y: auto;
}

.poster-report-btn {
  position: absolute;
  bottom: 0.4rem;
  right: 0.4rem;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #a1a1aa;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  z-index: 1;
  &:hover {
    color: #f43f5e;
    background: rgba(0, 0, 0, 0.7);
  }
}

.img-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}
.img-thumb-add {
  background: #18181b;
  border: 2px dashed #3f3f46;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  &:hover { border-color: #52525b; }
}
.img-thumb-remove {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0,0,0,0.7);
  border: none;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

/* Multiselect dark theme */
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
