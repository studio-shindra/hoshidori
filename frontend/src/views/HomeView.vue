<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  IconChevronLeft, IconChevronRight, IconCoffee,
  IconMessage, IconSparkles,
} from '@tabler/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import AppLoader from '@/components/AppLoader.vue'
import ShopCard from '@/components/ShopCard.vue'
import TicketCard from '@/components/TicketCard.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { ratingLabel } from '@/lib/rating'

const auth = useAuthStore()
const loading = ref(true)
const plannedLogs = ref([])
const watchedLogs = ref([])
const calendarLogs = ref([])
const plannedCount = ref(0)
const watchedCount = ref(0)
const calendarLoading = ref(false)
const featuredShops = ref([])
const recognizedShops = ref([])
const latestReviews = ref([])
const currentMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const selectedDate = ref(formatDate(new Date()))
const logFilter = ref('planned')

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const logsByDate = computed(() => {
  const map = new Map()
  for (const log of calendarLogs.value) {
    if (!log.watched_on) continue
    if (!map.has(log.watched_on)) map.set(log.watched_on, [])
    map.get(log.watched_on).push(log)
  }
  return map
})
const monthLabel = computed(() => new Intl.DateTimeFormat('ja-JP', {
  year: 'numeric', month: 'long',
}).format(currentMonth.value))
const calendarDays = computed(() => {
  const first = currentMonth.value
  const start = new Date(first.getFullYear(), first.getMonth(), 1 - first.getDay())
  return Array.from({ length: 42 }, (_, i) => {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    const key = formatDate(date)
    return {
      key,
      day: date.getDate(),
      current: date.getMonth() === first.getMonth(),
      today: key === formatDate(new Date()),
      logs: logsByDate.value.get(key) || [],
    }
  })
})
const selectedLogs = computed(() => (logsByDate.value.get(selectedDate.value) || [])
  .slice().sort((a, b) => (a.watched_time || '').localeCompare(b.watched_time || '')))
const filteredLogs = computed(() => {
  const logs = logFilter.value === 'planned' ? plannedLogs.value : watchedLogs.value
  return logs.slice().sort((a, b) => {
    const aKey = `${a.watched_on || ''}${a.watched_time || ''}`
    const bKey = `${b.watched_on || ''}${b.watched_time || ''}`
    return logFilter.value === 'planned' ? aKey.localeCompare(bKey) : bKey.localeCompare(aKey)
  })
})

async function moveMonth(offset) {
  currentMonth.value = new Date(
    currentMonth.value.getFullYear(), currentMonth.value.getMonth() + offset, 1,
  )
  selectedDate.value = formatDate(currentMonth.value)
  await fetchCalendar()
}

async function goToday() {
  const today = new Date()
  currentMonth.value = new Date(today.getFullYear(), today.getMonth(), 1)
  selectedDate.value = formatDate(today)
  await fetchCalendar()
}

async function fetchCalendar() {
  if (!auth.isAuthenticated) return
  calendarLoading.value = true
  try {
    const year = currentMonth.value.getFullYear()
    const month = currentMonth.value.getMonth() + 1
    const data = await api.getFresh(`/api/viewing-logs/calendar/?year=${year}&month=${month}`)
    calendarLogs.value = data.results || []
  } catch {
    calendarLogs.value = []
  } finally {
    calendarLoading.value = false
  }
}

async function fetchData() {
  loading.value = true
  await auth.fetchMe()
  const publicFetches = [
    api.get('/api/shops/featured/').then((d) => { featuredShops.value = d.results || d }).catch(() => {}),
    api.get('/api/shops/recognized/').then((d) => {
      const shops = d.results || d
      recognizedShops.value = shops.map((shop) => ({ ...shop, listing_tier: 'recognized' }))
    }).catch(() => {}),
    api.get('/api/reviews/latest/').then((d) => { latestReviews.value = d.results || d }).catch(() => {}),
  ]
  const privateFetches = auth.isAuthenticated ? [
    api.getFresh('/api/viewing-logs/?status=planned&scope=upcoming').then((d) => {
      const results = d.results || d
      plannedLogs.value = results.slice(0, 5)
      plannedCount.value = d.count ?? results.length
    }),
    api.getFresh('/api/viewing-logs/?status=watched&scope=recent').then((d) => {
      const results = d.results || d
      watchedLogs.value = results.slice(0, 5)
      watchedCount.value = d.count ?? results.length
    }),
    fetchCalendar(),
  ] : []
  await Promise.allSettled([...publicFetches, ...privateFetches])
  loading.value = false
}

onMounted(fetchData)
</script>

<template>
  <div class="home-page pb-4">
    <AppLoader v-if="loading" />
    <template v-else>
      <section v-if="!auth.isAuthenticated" class="welcome-panel text-center">
        <h1 class="welcome-title fw-bold">
          <span>観劇の予定と記憶を</span>
          <span>ホシドる</span>
        </h1>
        <p class="welcome-copy text-secondary mx-auto">観る日を決めて、感想を残して、終演後の一杯まで。</p>
        <div class="d-flex gap-2 justify-content-center mt-3">
          <RouterLink to="/register" class="btn btn-primary-rose px-4">はじめる</RouterLink>
          <RouterLink to="/login" class="btn btn-dark px-4">ログイン</RouterLink>
        </div>
      </section>

      <section class="calendar-panel mb-4" :class="{ 'calendar-public': !auth.isAuthenticated, 'calendar-loading': calendarLoading }">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h1 class="fs-4 fw-bold mb-0">{{ monthLabel }}</h1>
            <div class="d-flex gap-1">
              <button class="calendar-today" @click="goToday">今日</button>
              <button class="calendar-nav" aria-label="前の月" @click="moveMonth(-1)"><IconChevronLeft :size="18" /></button>
              <button class="calendar-nav" aria-label="次の月" @click="moveMonth(1)"><IconChevronRight :size="18" /></button>
            </div>
          </div>
          <div class="calendar-weekdays">
            <span v-for="day in ['日','月','火','水','木','金','土']" :key="day">{{ day }}</span>
          </div>
          <div class="calendar-grid">
            <button
              v-for="day in calendarDays"
              :key="day.key"
              class="calendar-day"
              :class="{ muted: !day.current, today: day.today, selected: selectedDate === day.key }"
              @click="selectedDate = day.key"
            >
              <span>{{ day.day }}</span>
              <div class="calendar-stars">
                <i v-for="log in day.logs.slice(0, 3)" :key="log.id" :class="log.status"></i>
              </div>
            </button>
          </div>
      </section>

      <template v-if="auth.isAuthenticated">
        <section v-if="selectedLogs.length" class="mb-4">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h2 class="fs-6 fw-bold mb-0">{{ selectedDate.replaceAll('-', '.') }} の観劇</h2>
          </div>
          <div class="d-flex flex-column gap-2">
            <TicketCard
              v-for="log in selectedLogs"
              :key="log.id"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :date="log.watched_on"
              :time="log.watched_time"
              :theater-name="log.theater_name"
              :theater-area="log.theater_area"
              :status="log.status"
              :after-shop-name="log.after_shop_name"
            />
          </div>
        </section>

        <section class="mb-4">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h2 class="fs-6 fw-bold mb-0">観劇一覧</h2>
            <RouterLink :to="{ path: '/mypage', query: { tab: logFilter } }" class="tiny text-secondary text-decoration-none">すべて見る →</RouterLink>
          </div>
          <div class="log-segments mb-3" role="tablist" aria-label="観劇一覧の絞り込み">
            <button
              type="button"
              :class="{ active: logFilter === 'planned' }"
              role="tab"
              :aria-selected="logFilter === 'planned'"
              @click="logFilter = 'planned'"
            >観る <span>{{ plannedCount }}</span></button>
            <button
              type="button"
              :class="{ active: logFilter === 'watched' }"
              role="tab"
              :aria-selected="logFilter === 'watched'"
              @click="logFilter = 'watched'"
            >観た <span>{{ watchedCount }}</span></button>
          </div>
          <div v-if="filteredLogs.length" class="d-flex flex-column gap-2">
            <TicketCard
              v-for="log in filteredLogs"
              :key="log.id"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :date="log.watched_on"
              :time="log.watched_time"
              :theater-name="log.theater_name"
              :theater-area="log.theater_area"
              :status="log.status"
              :after-shop-name="log.after_shop_name"
              compact
            />
          </div>
          <div v-else class="empty-ticket text-center">
            <IconSparkles :size="22" class="mb-2" />
            <p class="small text-secondary mb-2">{{ logFilter === 'planned' ? 'これから観る作品はまだありません' : '観た作品はまだありません' }}</p>
            <RouterLink to="/works" class="small color-rose">作品を探す →</RouterLink>
          </div>
        </section>
      </template>

      <section v-if="featuredShops.length" class="mb-4">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h2 class="d-flex align-items-center gap-2 fs-6 fw-bold mb-0"><IconCoffee :size="18" />終演後の候補</h2>
          <RouterLink to="/shops" class="text-secondary small text-decoration-none">すべて見る →</RouterLink>
        </div>
        <div class="d-flex gap-2 overflow-auto scroll-hide align-items-stretch">
          <div v-for="shop in featuredShops" :key="shop.id" class="shop-wrap flex-shrink-0 d-flex">
            <ShopCard :shop="shop" />
          </div>
        </div>
      </section>

      <section v-if="latestReviews.length" class="mb-4">
        <h2 class="d-flex align-items-center gap-2 fs-6 fw-bold mb-3"><IconMessage :size="18" />みんなの感激</h2>
        <div class="review-scroller d-flex gap-3 scroll-hide">
          <RouterLink v-for="review in latestReviews" :key="review.id" :to="`/works/${review.work_slug}`" class="review-note text-decoration-none flex-shrink-0">
            <div class="d-flex align-items-center gap-2">
              <div class="fw-bold text-white text-truncate">{{ review.work_title }}</div>
              <span v-if="review.rating_overall" class="review-rating ms-auto">{{ ratingLabel(review.rating_overall) }}</span>
            </div>
            <div class="tiny text-secondary text-truncate">{{ review.theater_name }}</div>
            <div v-if="review.after_shop_name" class="review-after mt-2">
              <IconSparkles :size="12" />感想戦：{{ review.after_shop_name }}
            </div>
            <div class="review-log d-flex align-items-start gap-2 mt-3 pt-2">
              <UserAvatar :src="review.user_avatar_url" :name="review.user_display_name" :size="22" class="flex-shrink-0" />
              <p class="small text-white-50 mb-0 review-body">{{ review.body }}</p>
            </div>
          </RouterLink>
        </div>
      </section>

      <section v-if="recognizedShops.length" class="recognized-section mb-4">
        <div class="d-flex align-items-end justify-content-between mb-3">
          <div>
            <div class="recognized-kicker">AFTER THE CURTAIN CALL</div>
            <h2 class="d-flex align-items-center gap-2 fs-6 fw-bold mb-0">
              <span class="recognized-mark" aria-hidden="true"></span>
              ホシドリ認定店
            </h2>
          </div>
          <RouterLink to="/shops" class="text-secondary small text-decoration-none">すべて見る →</RouterLink>
        </div>
        <p class="recognized-copy">観劇のあとに立ち寄りたい、劇場近くのお店。</p>
        <div class="d-flex gap-2 overflow-auto scroll-hide align-items-stretch">
          <div v-for="shop in recognizedShops" :key="shop.id" class="shop-wrap flex-shrink-0 d-flex">
            <ShopCard :shop="shop" />
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.home-page { padding-top: 1rem; }
.welcome-panel { position: relative; padding: 3.35rem .5rem 2.15rem; overflow: hidden; }
.welcome-title { display: flex; flex-direction: column; gap: .12rem; margin: 0; font-size: 1.18rem; letter-spacing: .035em; }
.welcome-copy { max-width: 360px; margin-top: .65rem; font-size: .72rem; white-space: nowrap; }
.calendar-panel { padding: 18px 14px; border: 1px solid rgba(255,255,255,.1); border-radius: 18px; background: radial-gradient(circle at top right, rgba(244,63,94,.12), transparent 38%), #121216; }
.calendar-public { margin-top: 0; }
.calendar-loading { opacity: .72; transition: opacity .15s; }
.calendar-nav { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; padding: 0; border: 1px solid rgba(255,255,255,.12); border-radius: 50%; background: rgba(255,255,255,.05); color: #fff; line-height: 1; }
.calendar-today { height: 34px; padding: 0 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 99px; background: rgba(255,255,255,.05); color: #d4d4d8; font-size: .72rem; font-weight: 700; }
.calendar-weekdays, .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); }
.calendar-weekdays span { padding: 6px 0; color: #71717a; font-size: .65rem; text-align: center; }
.calendar-day { min-height: 49px; padding: 6px 2px; border: 1px solid transparent; border-radius: 10px; background: transparent; color: #d4d4d8; font-size: .72rem; }
.calendar-day.muted { color: #3f3f46; }
.calendar-day.today { color: #fda4af; font-weight: 800; }
.calendar-day.selected { border-color: rgba(244,63,94,.45); background: rgba(244,63,94,.1); color: #fff; }
.calendar-stars { display: flex; justify-content: center; gap: 2px; min-height: 6px; margin-top: 5px; }
.calendar-stars i { width: 5px; height: 5px; border-radius: 50%; background: #f43f5e; box-shadow: 0 0 7px rgba(244,63,94,.7); }
.calendar-stars i.watched { background: #f59e0b; box-shadow: 0 0 7px rgba(245,158,11,.65); }
.empty-ticket { padding: 2rem; border: 1px dashed rgba(255,255,255,.14); border-radius: 14px; color: #52525b; }
.log-segments { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; padding: 4px; border-radius: 12px; background: #18181b; }
.log-segments button { padding: 9px; border: 0; border-radius: 9px; background: transparent; color: #71717a; font-size: .78rem; font-weight: 700; }
.log-segments button.active { background: #3f3f46; color: #fff; }
.log-segments span { margin-left: 3px; color: #a1a1aa; font-size: .68rem; }
.shop-wrap { width: 210px; }
.review-note { width: min(calc(100vw - 40px), 310px); padding: 14px; border: 1px solid rgba(255,255,255,.1); border-radius: 14px; background: #18181b; }
.review-scroller { width: 100%; padding-bottom: .35rem; overflow-x: auto; overflow-y: hidden; overscroll-behavior-x: contain; scroll-snap-type: x proximity; touch-action: pan-x; -webkit-overflow-scrolling: touch; }
.review-scroller .review-note { scroll-snap-align: start; }
.review-after { display: flex; align-items: center; gap: 4px; color: #fda4af; font-size: .72rem; font-weight: 700; }
.review-rating { padding: 2px 7px; border-radius: 99px; background: rgba(245,158,11,.12); color: #fbbf24; font-size: .65rem; font-weight: 700; }
.review-log { border-top: 1px solid rgba(255,255,255,.08); }
.review-body { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.recognized-section { padding-top: .35rem; }
.recognized-kicker { margin-bottom: .25rem; color: #f43f5e; font-size: .52rem; font-weight: 800; letter-spacing: .13em; }
.recognized-mark { width: 20px; height: 20px; flex: 0 0 auto; background: #fff; filter: drop-shadow(0 0 5px rgba(244,63,94,.7)); -webkit-mask: url('/icon.svg') center / contain no-repeat; mask: url('/icon.svg') center / contain no-repeat; }
.recognized-copy { margin: -.25rem 0 .85rem 1.75rem; color: #71717a; font-size: .66rem; }
@media (max-width: 360px) {
  .welcome-copy { font-size: .66rem; }
}
</style>
