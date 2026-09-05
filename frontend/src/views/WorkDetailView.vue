<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import Multiselect from '@vueform/multiselect'
import {
  IconCalendarEvent, IconCamera, IconHeart, IconHeartFilled,
  IconDots, IconExternalLink, IconFlag, IconMapPin, IconPencil, IconSparkles,
  IconStarFilled, IconTicket, IconUserOff, IconX,
} from '@tabler/icons-vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import AppLoader from '@/components/AppLoader.vue'
import RatingButtons from '@/components/RatingButtons.vue'
import ShopCard from '@/components/ShopCard.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { ratingIcon, ratingLabel } from '@/lib/rating'
import { IconThumbUp, IconHeartHandshake } from '@tabler/icons-vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
const MAX_FILE_SIZE = 10 * 1024 * 1024
const MAX_IMAGES = 4
const ratingIcons = { IconThumbUp, IconHeartHandshake, IconSparkles }

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const work = ref(null)
const performances = ref([])
const reviews = ref([])
const nearbyShops = ref([])
const loading = ref(true)

const showLogForm = ref(false)
const logPerf = ref('')
const logStatus = ref('planned')
const logWatchedOn = ref('')
const logWatchedTime = ref('')
const logMemo = ref('')
const logRating = ref('')
const logAfterShop = ref('')
const logSpoiler = ref(false)
const logError = ref('')
const logLoading = ref(false)
const logSuccess = ref('')
const logImages = ref([])
const logImageInput = ref(null)
const activeReviewMenuId = ref(null)
const reportingReview = ref(null)
const reportReason = ref('harassment')
const reportDetails = ref('')
const reportError = ref('')
const reportLoading = ref(false)
const moderationNotice = ref('')
const todayDate = formatDate(new Date())

const perfOptions = computed(() => performances.value.map((performance) => ({
  value: performance.id,
  label: [performance.theater_name, performance.start_date, performance.company_name].filter(Boolean).join(' / '),
})))
const theaterSlug = computed(() => performances.value[0]?.theater_slug || null)
const theaterName = computed(() => performances.value[0]?.theater_name || '')
const companyName = computed(() => performances.value[0]?.company_name || '')
const dateRange = computed(() => {
  const performance = performances.value[0]
  if (!performance) return ''
  if (performance.start_date === performance.end_date) return performance.start_date
  return [performance.start_date, performance.end_date].filter(Boolean).join(' 〜 ')
})
const compactDateRange = computed(() => {
  const performance = performances.value[0]
  if (!performance?.start_date) return ''
  const start = performance.start_date.replaceAll('-', '.')
  if (!performance.end_date || performance.start_date === performance.end_date) return start
  const end = performance.end_date.startsWith(performance.start_date.slice(0, 4))
    ? performance.end_date.slice(5).replace('-', '.')
    : performance.end_date.replaceAll('-', '.')
  return `${start}–${end}`
})
const allCasts = computed(() => {
  const castMap = new Map()
  for (const performance of performances.value) {
    for (const cast of performance.casts || []) {
      if (!castMap.has(cast.person)) castMap.set(cast.person, { name: cast.person_name, role: cast.role_name })
    }
  }
  return Array.from(castMap.values())
})
const averageRating = computed(() => {
  const rated = reviews.value.filter((review) => review.rating_overall)
  if (!rated.length) return null
  return (rated.reduce((sum, review) => sum + review.rating_overall, 0) / rated.length).toFixed(1)
})
const tierOrder = { sponsored: 0, recognized: 1, listed: 2, google: 3 }
const sortedShops = computed(() => [...nearbyShops.value]
  .sort((a, b) => (tierOrder[a.listing_tier] ?? 9) - (tierOrder[b.listing_tier] ?? 9)))
const sponsoredShops = computed(() => sortedShops.value.filter((shop) => shop.listing_tier === 'sponsored'))
const recognizedShops = computed(() => sortedShops.value.filter((shop) => shop.listing_tier === 'recognized'))
const listedShops = computed(() => sortedShops.value.filter((shop) => shop.listing_tier === 'listed'))
const googleShops = computed(() => sortedShops.value.filter((shop) => shop.source === 'google_places'))
const googleNearbyUrl = computed(() => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${theaterName.value} 周辺 飲食店`)}`)
const shopOptions = computed(() => sortedShops.value
  .filter((shop) => shop.source !== 'google_places')
  .map((shop) => ({
  value: shop.id,
  label: [shop.name, shop.distance_note || shop.category].filter(Boolean).join(' / '),
})))
const heroStyle = computed(() => {
  const key = work.value?.slug || 'hoshidori'
  let hash = 7
  for (const character of key) hash = (hash * 31 + character.charCodeAt(0)) >>> 0
  return {
    '--blob-one-x': `${14 + (hash % 68)}%`,
    '--blob-one-y': `${18 + ((hash >>> 5) % 42)}%`,
    '--blob-two-x': `${12 + ((hash >>> 10) % 72)}%`,
    '--blob-two-y': `${30 + ((hash >>> 15) % 42)}%`,
  }
})

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

async function fetchShops() {
  if (!theaterSlug.value) return
  try {
    const data = await api.getFresh(`/api/theaters/${theaterSlug.value}/shops/?include_google=1&preview_google=1`)
    nearbyShops.value = data.results || data
  } catch {
    nearbyShops.value = []
  }
}

onMounted(async () => {
  try {
    const slug = route.params.slug
    work.value = await api.get(`/api/works/${slug}/`)
    const [performanceData, reviewData] = await Promise.all([
      api.get(`/api/performances/?work=${work.value.id}`),
      api.get(`/api/reviews/?work=${work.value.id}`),
    ])
    performances.value = performanceData.results || performanceData
    reviews.value = reviewData.results || reviewData
    await fetchShops()
  } catch (error) {
    if (error.status === 404) router.replace({ name: 'not-found' })
  } finally {
    loading.value = false
  }
})

function openLogForm(status) {
  showLogForm.value = true
  logStatus.value = status
  logPerf.value = performances.value.length === 1 ? performances.value[0].id : ''
  logWatchedOn.value = status === 'watched'
    ? formatDate(new Date())
    : (performances.value[0]?.start_date || '')
  logError.value = ''
  logSuccess.value = ''
}

function onLogImageSelect(event) {
  for (const file of Array.from(event.target.files)) {
    if (logImages.value.length >= MAX_IMAGES) break
    if (!file.type.startsWith('image/') || file.size > MAX_FILE_SIZE) continue
    logImages.value.push({ file, preview: URL.createObjectURL(file) })
  }
  event.target.value = ''
}

function removeLogImage(index) {
  URL.revokeObjectURL(logImages.value[index].preview)
  logImages.value.splice(index, 1)
}

async function uploadLogImages(logId) {
  for (let index = 0; index < logImages.value.length; index++) {
    const formData = new FormData()
    formData.append('file', logImages.value[index].file)
    formData.append('upload_preset', UPLOAD_PRESET)
    const response = await fetch(`https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`, {
      method: 'POST', body: formData,
    })
    if (!response.ok) continue
    const image = await response.json()
    await api.post(`/api/viewing-logs/${logId}/images/`, {
      image_url: image.secure_url,
      image_public_id: image.public_id,
      image_width: image.width,
      image_height: image.height,
      image_format: image.format,
      order: index,
    })
  }
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
      watched_on: logWatchedOn.value || null,
      watched_time: logWatchedTime.value || null,
      after_shop: logStatus.value === 'watched' && logAfterShop.value ? Number(logAfterShop.value) : null,
    }
    const log = await api.post('/api/viewing-logs/', body)
    if (logImages.value.length && logStatus.value === 'watched') await uploadLogImages(log.id)
    if (logMemo.value.trim() && logStatus.value === 'watched') {
      const reviewBody = {
        performance: Number(logPerf.value),
        body: logMemo.value,
        is_spoiler: logSpoiler.value,
      }
      if (logRating.value) reviewBody.rating_overall = Number(logRating.value)
      const newReview = await api.post('/api/reviews/', reviewBody)
      newReview.after_shop = body.after_shop
      newReview.after_shop_name = sortedShops.value.find((shop) => shop.id === body.after_shop)?.name || null
      newReview.after_shop_slug = sortedShops.value.find((shop) => shop.id === body.after_shop)?.slug || null
      reviews.value.unshift(newReview)
    }
    logSuccess.value = 'ホシに記録しました'
    logMemo.value = ''
    logRating.value = ''
    logAfterShop.value = ''
    logSpoiler.value = false
    for (const image of logImages.value) URL.revokeObjectURL(image.preview)
    logImages.value = []
    showLogForm.value = false
  } catch (error) {
    logError.value = error.data ? Object.values(error.data).flat().join(' ') : '保存に失敗しました'
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
    // Keep the current visual state if the request fails.
  }
}

function openReport(review) {
  reportingReview.value = review
  reportReason.value = 'harassment'
  reportDetails.value = ''
  reportError.value = ''
  activeReviewMenuId.value = null
}

async function submitReport() {
  if (!reportingReview.value) return
  reportLoading.value = true
  reportError.value = ''
  try {
    await api.post(`/api/reviews/${reportingReview.value.id}/report/`, {
      reason: reportReason.value,
      details: reportDetails.value,
    })
    reportingReview.value = null
    moderationNotice.value = '通報を受け付けました。内容を確認します。'
  } catch (error) {
    reportError.value = error.data ? Object.values(error.data).flat().join(' ') : '通報を送信できませんでした'
  } finally {
    reportLoading.value = false
  }
}

async function blockReviewUser(review) {
  activeReviewMenuId.value = null
  if (!confirm(`${review.user_display_name}さんをブロックしますか？\nこのユーザーの投稿は表示されなくなります。`)) return
  try {
    await api.post(`/api/reviews/${review.id}/block-user/`)
    reviews.value = reviews.value.filter((item) => item.user_id !== review.user_id)
    moderationNotice.value = `${review.user_display_name}さんをブロックしました。`
  } catch {
    moderationNotice.value = 'ブロックできませんでした。時間をおいてお試しください。'
  }
}
</script>

<template>
  <div class="pb-5">
    <AppLoader v-if="loading" />
    <template v-else-if="work">
      <section class="work-ticket-hero" :style="heroStyle">
        <div class="work-hero-content">
          <h1 class="work-title fs-3 fw-bold">{{ work.title }}</h1>
          <div class="work-meta d-flex flex-wrap small">
            <span :class="{ 'missing-meta': !dateRange }">
              <IconCalendarEvent :size="14" />{{ compactDateRange || '公演日 未入力' }}
              <RouterLink v-if="!dateRange && auth.isAuthenticated" :to="`/works/${work.slug}/edit`" class="inline-input-link">入力</RouterLink>
            </span>
            <span :class="{ 'missing-meta': !theaterName }">
              <IconMapPin :size="14" />{{ theaterName || '劇場 未入力' }}
              <RouterLink v-if="!theaterName && auth.isAuthenticated" :to="`/works/${work.slug}/edit`" class="inline-input-link">入力</RouterLink>
            </span>
          </div>
          <div class="company-line small mt-2" :class="companyName ? 'text-secondary' : 'missing-meta'">
            {{ companyName || '団体名 未入力' }}
            <RouterLink v-if="!companyName && auth.isAuthenticated" :to="`/works/${work.slug}/edit`" class="inline-input-link">入力</RouterLink>
          </div>

          <div class="cast-line mt-3">
            <span class="cast-label">出演者</span>
            <div v-if="allCasts.length" class="d-flex flex-wrap gap-1">
              <RouterLink
                v-for="cast in allCasts"
                :key="cast.name"
                :to="{ path: '/works', query: { person: cast.name } }"
                class="cast-pill text-decoration-none"
              >{{ cast.name }}<span v-if="cast.role" class="opacity-50"> / {{ cast.role }}</span></RouterLink>
            </div>
            <div v-else class="missing-cast-inline">
              未入力
              <RouterLink :to="`/works/${work.slug}/edit`" class="inline-pencil-link" aria-label="出演者を編集">
                <IconPencil :size="12" />
              </RouterLink>
            </div>
          </div>

          <div v-if="auth.isAuthenticated" class="d-flex justify-content-end mt-3">
            <RouterLink :to="`/works/${work.slug}/edit`" class="wiki-edit-link">
              <IconPencil :size="12" />作品情報を編集
            </RouterLink>
          </div>
        </div>
      </section>

      <p v-if="work.description" class="work-description mt-3 mb-0">{{ work.description }}</p>
      <RouterLink
        v-else-if="auth.isAuthenticated"
        :to="`/works/${work.slug}/edit`"
        class="missing-description mt-3"
      ><IconPencil :size="11" />作品説明 未入力</RouterLink>
      <span v-else class="missing-description mt-3">作品説明 未入力</span>

      <template v-if="auth.isAuthenticated">
        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-light flex-fill d-flex align-items-center justify-content-center" @click="openLogForm('planned')">
            <IconTicket :size="16" class="me-1" />観る予定
          </button>
          <button class="btn btn-primary-rose flex-fill d-flex align-items-center justify-content-center" @click="openLogForm('watched')">
            <IconStarFilled :size="16" class="me-1" />観た
          </button>
        </div>
        <p v-if="logSuccess" class="record-success mb-0">{{ logSuccess }}</p>
      </template>
      <RouterLink v-else :to="{ name: 'login', query: { next: route.fullPath } }" class="d-block text-secondary small mt-3">ログインして予定・感想を記録 →</RouterLink>

      <Teleport to="body">
        <Transition name="fade">
          <div v-if="showLogForm" class="log-modal-backdrop" @click.self="showLogForm = false">
            <div class="log-modal">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h2 class="small fw-semibold mb-0">{{ logStatus === 'planned' ? '観る予定を入れる' : '観劇をホシにする' }}</h2>
                <button type="button" class="btn-close btn-close-white" aria-label="記録画面を閉じる" @click="showLogForm = false"></button>
              </div>
              <form class="d-flex flex-column gap-3" @submit.prevent="submitLog">
                <div>
                  <label class="form-label tiny text-secondary">公演</label>
                  <Multiselect v-model="logPerf" :options="perfOptions" :searchable="true" placeholder="公演を選ぶ" class="multiselect-dark" />
                </div>
                <div>
                  <label class="form-label tiny text-secondary">{{ logStatus === 'watched' ? '観劇日時' : '観劇予定日時' }}</label>
                  <div class="d-flex gap-2">
                    <input v-model="logWatchedOn" required type="date" :max="logStatus === 'watched' ? todayDate : undefined" class="form-control bg-dark border-secondary text-light form-control-sm" />
                    <input v-model="logWatchedTime" type="time" class="form-control bg-dark border-secondary text-light form-control-sm time-input" />
                  </div>
                </div>
                <div>
                  <label class="form-label tiny text-secondary">感想・メモ</label>
                  <textarea v-model="logMemo" :rows="logStatus === 'watched' ? 4 : 2" placeholder="観劇の記憶を残す（任意）" class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
                </div>
                <template v-if="logStatus === 'watched'">
                  <div>
                    <label class="form-label tiny text-secondary d-flex align-items-center gap-1"><IconSparkles :size="12" />その後行った店（任意）</label>
                    <Multiselect v-model="logAfterShop" :options="shopOptions" :searchable="true" :can-clear="true" placeholder="感想戦をした店を選ぶ" class="multiselect-dark" />
                  </div>
                  <div>
                    <label class="form-label tiny text-secondary">評価（任意）</label>
                    <RatingButtons v-model="logRating" />
                  </div>
                  <div>
                    <label class="form-label tiny text-secondary">自分の観劇写真（最大{{ MAX_IMAGES }}枚）</label>
                    <p class="tiny text-secondary">自分で撮影し、公開してよい写真だけ。舞台・ポスターの転載はできません。</p>
                    <input ref="logImageInput" type="file" accept="image/*" multiple class="d-none" @change="onLogImageSelect" />
                    <div class="d-flex gap-2 flex-wrap">
                      <div v-for="(image, index) in logImages" :key="image.preview" class="img-thumb">
                        <img :src="image.preview" class="w-100 h-100 object-fit-cover rounded" />
                        <button type="button" class="img-thumb-remove" :aria-label="`写真${index + 1}を削除`" @click="removeLogImage(index)"><IconX :size="12" /></button>
                      </div>
                      <button v-if="logImages.length < MAX_IMAGES" type="button" class="img-thumb img-thumb-add" aria-label="写真を追加" @click="logImageInput?.click()"><IconCamera :size="20" class="text-secondary" /></button>
                    </div>
                  </div>
                  <div class="form-check">
                    <input id="detailSpoiler" v-model="logSpoiler" type="checkbox" class="form-check-input" />
                    <label for="detailSpoiler" class="form-check-label small text-secondary">ネタバレを含む</label>
                  </div>
                </template>
                <p v-if="logError" class="small text-danger mb-0">{{ logError }}</p>
                <div class="d-flex gap-2">
                  <button class="btn btn-primary-rose btn-sm flex-fill" :disabled="logLoading">{{ logLoading ? '保存中...' : '保存' }}</button>
                  <button type="button" class="btn btn-dark btn-sm flex-fill text-secondary" @click="showLogForm = false">閉じる</button>
                </div>
              </form>
            </div>
          </div>
        </Transition>
      </Teleport>

      <Teleport to="body">
        <Transition name="fade">
          <div v-if="reportingReview" class="log-modal-backdrop" @click.self="reportingReview = null">
            <form class="log-modal d-flex flex-column gap-3" @submit.prevent="submitReport">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h2 class="small fw-semibold mb-1">この投稿を通報</h2>
                  <p class="tiny text-secondary mb-0">運営が内容を確認し、必要に応じて対応します。</p>
                </div>
                <button type="button" class="btn-close btn-close-white" aria-label="通報画面を閉じる" @click="reportingReview = null"></button>
              </div>
              <div>
                <label class="form-label tiny text-secondary">理由</label>
                <select v-model="reportReason" class="form-select bg-dark border-secondary text-light form-select-sm">
                  <option value="spam">スパム・宣伝</option>
                  <option value="harassment">嫌がらせ・誹謗中傷</option>
                  <option value="hate">差別的な表現</option>
                  <option value="sexual">性的・不適切な内容</option>
                  <option value="copyright">権利侵害</option>
                  <option value="other">その他</option>
                </select>
              </div>
              <div>
                <label class="form-label tiny text-secondary">補足（任意）</label>
                <textarea v-model="reportDetails" rows="3" maxlength="1000" class="form-control bg-dark border-secondary text-light form-control-sm" placeholder="問題だと思う点を教えてください"></textarea>
              </div>
              <p v-if="reportError" class="small text-danger mb-0">{{ reportError }}</p>
              <button class="btn btn-primary-rose btn-sm" :disabled="reportLoading">{{ reportLoading ? '送信中...' : '通報する' }}</button>
            </form>
          </div>
        </Transition>
      </Teleport>

      <section class="mt-5">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h2 class="fs-6 fw-bold mb-0">観劇メモ <span v-if="reviews.length" class="text-secondary">{{ reviews.length }}</span></h2>
          <span v-if="averageRating" class="rating-average">評価 {{ averageRating }}</span>
        </div>
        <p v-if="moderationNotice" class="moderation-notice">{{ moderationNotice }}</p>
        <div v-if="reviews.length" class="d-flex flex-column gap-3">
          <article v-for="review in reviews" :key="review.id" class="review-card">
            <div class="d-flex align-items-center gap-2">
              <UserAvatar :src="review.user_avatar_url" :name="review.user_display_name" :size="28" />
              <span class="small fw-medium">{{ review.user_display_name }}</span>
              <div class="review-head-actions ms-auto">
                <span v-if="review.rating_overall" class="review-rating">
                  <component :is="ratingIcons[ratingIcon(review.rating_overall)]" :size="13" />{{ ratingLabel(review.rating_overall) }}
                </span>
                <button
                  v-if="auth.isAuthenticated && review.user_id !== auth.user?.id"
                  class="review-menu-button"
                  aria-label="投稿メニュー"
                  @click="activeReviewMenuId = activeReviewMenuId === review.id ? null : review.id"
                ><IconDots :size="17" /></button>
              </div>
              <div v-if="activeReviewMenuId === review.id" class="review-action-menu">
                <button @click="openReport(review)"><IconFlag :size="14" />この投稿を通報</button>
                <button @click="blockReviewUser(review)"><IconUserOff :size="14" />このユーザーをブロック</button>
              </div>
            </div>
            <p v-if="review.is_spoiler" class="tiny color-rose mt-2 mb-0">ネタバレあり</p>
            <p class="small text-light lh-base py-2 my-2 border-top border-secondary">{{ review.body }}</p>
            <div class="d-flex align-items-center justify-content-between gap-3">
              <RouterLink v-if="review.after_shop_slug" :to="`/shops/${review.after_shop_slug}`" class="after-shop-link"><IconSparkles :size="12" />感想戦：{{ review.after_shop_name }}</RouterLink>
              <span v-else></span>
              <button class="review-like btn btn-link btn-sm p-0 text-decoration-none" :aria-label="review.is_liked ? 'いいねを取り消す' : 'いいねする'" :class="review.is_liked ? 'color-rose' : 'text-secondary'" @click="toggleLike(review)">
                <component :is="review.is_liked ? IconHeartFilled : IconHeart" :size="15" /> {{ review.like_count || 0 }}
              </button>
            </div>
          </article>
        </div>
        <div v-else class="empty-reviews text-center">
          <p class="text-secondary small mb-2">まだ観劇メモはありません</p>
          <button v-if="auth.isAuthenticated" class="btn btn-sm btn-outline-secondary" @click="openLogForm('watched')">最初のホシを残す</button>
        </div>
      </section>

      <section class="mt-5" v-if="sortedShops.length">
        <div class="mb-3">
          <div class="tiny color-rose fw-bold text-uppercase">After the curtain call</div>
          <h2 class="fs-5 fw-bold mb-1">終演後、どこ行く？</h2>
          <p class="small text-secondary mb-0">{{ theaterName }}から歩いて行ける、感想戦の候補。</p>
        </div>
        <div v-if="sponsoredShops.length" class="shop-tier-block sponsored-block mb-4">
          <div class="d-flex flex-column gap-3">
            <ShopCard v-for="shop in sponsoredShops" :key="shop.id" :shop="shop" />
          </div>
        </div>
        <div v-if="recognizedShops.length" class="shop-tier-block recognized-block mb-4">
          <div class="d-flex flex-column gap-3">
            <ShopCard v-for="shop in recognizedShops" :key="shop.id" :shop="shop" />
          </div>
        </div>
        <div v-if="listedShops.length" class="shop-tier-block recognized-block mb-4">
          <div class="d-flex flex-column gap-3">
            <ShopCard v-for="shop in listedShops" :key="shop.id" :shop="shop" />
          </div>
        </div>
        <div v-if="googleShops.length" class="shop-tier-block google-block">
          <div class="d-flex justify-content-end mb-1">
            <a :href="googleNearbyUrl" target="_blank" rel="noopener noreferrer" class="google-attribution" translate="no">
              Google Mapsで見る<IconExternalLink :size="12" />
            </a>
          </div>
          <div class="d-flex flex-column">
            <ShopCard v-for="shop in googleShops" :key="shop.id" :shop="shop" />
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
<style scoped>
.work-ticket-hero { position: relative; display: flex; min-height: 285px; margin-top: calc(-1rem - var(--header-height) - env(safe-area-inset-top)); padding: calc(92px + env(safe-area-inset-top)) 22px 18px; align-items: stretch; overflow: hidden; border: 0; border-radius: 0 0 22px 22px; background: radial-gradient(circle at var(--blob-one-x) var(--blob-one-y), rgba(244,63,94,.2), transparent 36%), radial-gradient(circle at var(--blob-two-x) var(--blob-two-y), rgba(99,102,241,.13), transparent 38%), linear-gradient(155deg, #25252d, #101014 72%); box-shadow: inset 0 -1px rgba(255,255,255,.1); }
.work-ticket-hero::before { content: ''; position: absolute; inset: 0 0 auto; height: 74px; background: linear-gradient(to bottom, #0a0a0b 0%, rgba(10,10,11,.66) 38%, rgba(10,10,11,0) 100%); backdrop-filter: blur(7px); pointer-events: none; }
.work-ticket-hero > * { position: relative; z-index: 1; }
.work-ticket-hero span { display: inline-flex; align-items: center; gap: 4px; }
.work-hero-content { display: flex; width: 100%; flex-direction: column; justify-content: flex-end; }
.work-title { margin-bottom: 1.05rem; }
.work-meta { flex-wrap: nowrap !important; gap: .55rem; font-size: .73rem; white-space: nowrap; }
.missing-meta { color: #71717a; }
.company-line { display: flex; align-items: center; gap: 6px; }
.inline-input-link { padding: 1px 6px; border: 1px solid rgba(255,255,255,.18); border-radius: 99px; color: #a1a1aa; font-size: .6rem; font-weight: 700; line-height: 1.4; text-decoration: none; }
.inline-input-link:hover { border-color: rgba(255,255,255,.32); color: #fff; }
.wiki-edit-link { display: inline-flex; align-items: center; gap: 4px; color: #a1a1aa; font-size: .66rem; text-decoration: none; }
.wiki-edit-link:hover { color: #fff; }
.cast-line { display: flex; align-items: flex-start; gap: 9px; }
.cast-label { flex-shrink: 0; padding-top: .25rem; color: #a1a1aa; font-size: .66rem; font-weight: 700; }
.cast-pill { padding: .25rem .55rem; border: 1px solid rgba(255,255,255,.14); border-radius: 99px; background: rgba(255,255,255,.06); color: #e4e4e7; font-size: .68rem; }
.missing-cast-inline { display: flex; align-items: center; gap: 6px; padding-top: .16rem; color: #71717a; font-size: .7rem; }
.inline-pencil-link { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border: 1px solid rgba(255,255,255,.18); border-radius: 50%; color: #a1a1aa; text-decoration: none; }
.inline-pencil-link:hover { border-color: rgba(255,255,255,.34); color: #fff; }
.work-description { color: #a1a1aa; font-size: .76rem; line-height: 1.75; white-space: pre-line; }
.missing-description { display: inline-flex; width: fit-content; align-items: center; gap: 4px; color: #52525b; font-size: .68rem; text-decoration: none; }
a.missing-description:hover { color: #a1a1aa; }
.time-input { max-width: 8rem; }
.review-card { position: relative; padding: 14px; border: 1px solid rgba(255,255,255,.09); border-radius: 13px; background: #18181b; }
.review-head-actions { display: flex; align-items: center; gap: 8px; }
.review-menu-button { display: grid; width: 28px; height: 28px; padding: 0; place-items: center; border: 0; border-radius: 50%; background: transparent; color: #71717a; }
.review-menu-button:active { background: rgba(255,255,255,.07); color: #fff; }
.review-action-menu { position: absolute; z-index: 10; top: 45px; right: 12px; min-width: 190px; overflow: hidden; border: 1px solid rgba(255,255,255,.12); border-radius: 11px; background: #242428; box-shadow: 0 12px 30px rgba(0,0,0,.35); }
.review-action-menu button { display: flex; width: 100%; align-items: center; gap: 8px; padding: .72rem .8rem; border: 0; border-bottom: 1px solid rgba(255,255,255,.07); background: transparent; color: #d4d4d8; font-size: .72rem; text-align: left; }
.review-action-menu button:last-child { border-bottom: 0; }
.review-action-menu button:active { background: rgba(255,255,255,.07); }
.moderation-notice { padding: .6rem .75rem; border: 1px solid rgba(244,63,94,.18); border-radius: 9px; background: rgba(244,63,94,.07); color: #fda4af; font-size: .7rem; }
.review-rating, .rating-average { display: inline-flex; align-items: center; gap: 3px; color: #f59e0b; font-size: .7rem; font-weight: 700; }
.rating-average { padding: .25rem .55rem; border-radius: 99px; background: rgba(245,158,11,.12); }
.after-shop-link { display: inline-flex; align-items: center; gap: 4px; color: #fda4af; font-size: .72rem; text-decoration: none; }
.review-like { display: inline-flex; align-items: center; gap: 4px; flex-shrink: 0; }
.google-attribution { display: inline-flex; align-items: center; gap: 4px; color: #a1a1aa; font-family: Roboto, sans-serif; font-size: .72rem; text-align: right; text-decoration: none; white-space: nowrap; }
.shop-tier-block { padding: 12px; border-radius: 15px; background: rgba(255,255,255,.025); }
.shop-tier-block.sponsored-block, .shop-tier-block.recognized-block { padding: 0; border: 0; background: transparent; }
.shop-tier-block.google-block { padding: 0; border: 0; background: transparent; }
.shop-tier-label { font-size: .7rem; font-weight: 800; letter-spacing: .04em; }
.empty-reviews { padding: 2rem; border: 1px dashed rgba(255,255,255,.13); border-radius: 13px; }
.record-success { margin-top: .65rem; color: #86efac; font-size: .72rem; text-align: center; }
.log-modal-backdrop { position: fixed; inset: 0; z-index: 100000; display: flex; align-items: flex-end; justify-content: center; padding: max(1rem, env(safe-area-inset-top)) 1rem max(1rem, env(safe-area-inset-bottom)); background: rgba(0,0,0,.76); }
.log-modal { width: 100%; max-width: 480px; max-height: 88vh; max-height: calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 2rem); overflow-y: auto; overscroll-behavior: contain; -webkit-overflow-scrolling: touch; padding: 1.25rem 1.25rem calc(1.25rem + env(safe-area-inset-bottom)); border: 1px solid rgba(255,255,255,.12); border-radius: 18px 18px 10px 10px; background: #18181b; }
.multiselect-dark {
  --ms-bg: #212529;
  --ms-bg-disabled: #212529;
  --ms-border-color: #52525b;
  --ms-border-color-active: #71717a;
  --ms-ring-color: rgba(244,63,94,.18);
  --ms-placeholder-color: #71717a;
  --ms-font-size: .8rem;
  --ms-option-bg-pointed: #3f3f46;
  --ms-option-color-pointed: #fff;
  --ms-option-bg-selected: #f43f5e;
  --ms-dropdown-bg: #212529;
  --ms-dropdown-border-color: #52525b;
  --ms-tag-bg: #f43f5e;
  color: #f4f4f5;
}
.img-thumb { position: relative; width: 64px; height: 64px; border: 1px dashed #52525b; border-radius: 8px; background: #27272a; }
.img-thumb-add { display: flex; align-items: center; justify-content: center; }
.img-thumb-remove { position: absolute; top: -6px; right: -6px; width: 20px; height: 20px; padding: 0; border: 0; border-radius: 50%; background: #f43f5e; color: #fff; }
</style>
