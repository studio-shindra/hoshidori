<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { cloudinaryUrl, IMG_THUMB } from '@/lib/cloudinary'
import {
  IconCalendarEvent, IconChevronRight, IconMapPin, IconPencil,
  IconPlus, IconSearch, IconTheater, IconUser,
} from '@tabler/icons-vue'
import AppLoader from '@/components/AppLoader.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const works = ref([])
const loading = ref(true)
const query = ref(route.query.person || '')
const searchType = ref(
  ['person', 'theater'].includes(route.query.mode)
    ? route.query.mode
    : (route.query.person ? 'person' : 'title'),
)
const popularPeople = ref([])
const theaters = ref([])
const theaterPlaces = ref({})
const theaterPhotoLoadingSlugs = ref(new Set())
const theatersLoading = ref(false)
const theatersLoadingMore = ref(false)
const theaterPage = ref(1)
const theaterHasNext = ref(false)
let theaterPhotoGeneration = 0

const peopleCountRange = computed(() => {
  const counts = popularPeople.value.map((person) => Number(person.work_count) || 1)
  return {
    min: counts.length ? Math.min(...counts) : 1,
    max: counts.length ? Math.max(...counts) : 1,
  }
})

function personTagStyle(person) {
  const count = Number(person.work_count) || 1
  const { min, max } = peopleCountRange.value
  const weight = max === min ? 0.45 : (count - min) / (max - min)
  return {
    fontSize: `${0.68 + (weight * 0.38)}rem`,
    color: `rgba(244,244,245,${0.58 + (weight * 0.42)})`,
    fontWeight: Math.round(520 + (weight * 220)),
  }
}

function theaterImage(theater) {
  const ownedImage = theater.image_url || theater.image
  return ownedImage
    ? cloudinaryUrl(ownedImage, IMG_THUMB)
    : theaterPlaces.value[theater.slug]?.photo_uri || ''
}

function usesGoogleTheaterImage(theater) {
  return !theater.image_url && !theater.image && !!theaterPlaces.value[theater.slug]?.photo_uri
}

async function fetchTheaterPhotos(batch, reset = false) {
  const generation = reset ? ++theaterPhotoGeneration : theaterPhotoGeneration
  const batchSlugs = batch.map((theater) => theater.slug)
  try {
    const chunks = []
    for (let index = 0; index < batch.length; index += 12) {
      chunks.push(batch.slice(index, index + 12))
    }
    if (!chunks.length) return
    if (reset) theaterPlaces.value = {}
    theaterPhotoLoadingSlugs.value = reset
      ? new Set(batchSlugs)
      : new Set([...theaterPhotoLoadingSlugs.value, ...batchSlugs])
    const responses = await Promise.all(chunks.map((chunk) => {
      const slugs = chunk.map((theater) => theater.slug).join(',')
      const url = `/api/theaters/google-places/?slugs=${encodeURIComponent(slugs)}`
      return api.getFresh(url).catch(() => ({}))
    }))
    if (generation !== theaterPhotoGeneration) return
    theaterPlaces.value = {
      ...theaterPlaces.value,
      ...Object.assign({}, ...responses),
    }
  } catch {
    if (generation === theaterPhotoGeneration && reset) theaterPlaces.value = {}
  } finally {
    if (generation === theaterPhotoGeneration) {
      const loadingSlugs = new Set(theaterPhotoLoadingSlugs.value)
      batchSlugs.forEach((slug) => loadingSlugs.delete(slug))
      theaterPhotoLoadingSlugs.value = loadingSlugs
    }
  }
}

async function fetchPopularPeople() {
  try {
    const data = await api.get('/api/people/popular/')
    popularPeople.value = data.results || data
  } catch {
    /* empty */
  }
}

async function fetchWorks() {
  loading.value = true
  try {
    const q = query.value.trim()
    if (searchType.value === 'person' && !q) {
      works.value = []
      return
    }
    let url = '/api/works/'
    if (q) {
      url = searchType.value === 'person'
        ? `/api/works/?person=${encodeURIComponent(q)}`
        : `/api/works/?q=${encodeURIComponent(q)}`
    }
    const data = await api.getFresh(url)
    works.value = data.results || data
  } catch {
    works.value = []
  } finally {
    loading.value = false
  }
}

async function fetchTheaters({ append = false } = {}) {
  if (append) theatersLoadingMore.value = true
  else theatersLoading.value = true
  try {
    const q = query.value.trim()
    const page = append ? theaterPage.value + 1 : 1
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (page > 1) params.set('page', String(page))
    const data = await api.getFresh(`/api/theaters/?${params.toString()}`)
    const results = data.results || data
    theaters.value = append ? [...theaters.value, ...results] : results
    theaterPage.value = page
    theaterHasNext.value = Boolean(data.next)
    fetchTheaterPhotos(results, !append)
  } catch {
    if (!append) theaters.value = []
  } finally {
    if (append) theatersLoadingMore.value = false
    else theatersLoading.value = false
  }
}

function submitSearch() {
  if (searchType.value === 'theater') fetchTheaters()
  else fetchWorks()
}

function searchByPerson(name) {
  searchType.value = 'person'
  query.value = name
  router.replace({ path: '/works', query: { mode: 'person', person: name } })
  fetchWorks()
}

function setSearchType(type) {
  searchType.value = type
  query.value = ''
  router.replace({ path: '/works', query: type === 'title' ? {} : { mode: type } })
  if (type === 'theater') fetchTheaters()
  else fetchWorks()
}

onMounted(() => {
  if (searchType.value === 'theater') fetchTheaters()
  else fetchWorks()
  fetchPopularPeople()
})
</script>

<template>
  <div class="works-search-page pt-4">
    <header class="mb-4">
      <h1 class="fw-bold fs-3 mb-1">探す</h1>
      <p class="small text-secondary mb-0">作品、出演者、劇場から舞台の記憶をたどる。</p>
    </header>

    <div class="search-mode mb-2">
      <button :class="{ active: searchType === 'title' }" @click="setSearchType('title')">作品名</button>
      <button :class="{ active: searchType === 'person' }" @click="setSearchType('person')"><IconUser :size="13" />出演者</button>
      <button :class="{ active: searchType === 'theater' }" @click="setSearchType('theater')"><IconTheater :size="13" />劇場</button>
    </div>

    <form class="work-search-form" @submit.prevent="submitSearch">
      <IconSearch :size="18" :stroke="1.6" />
      <input
        v-model="query"
        type="search"
        :placeholder="searchType === 'person' ? '出演者名を入力' : searchType === 'theater' ? '劇場名を入力' : '作品名を入力'"
        :aria-label="searchType === 'person' ? '出演者を検索' : searchType === 'theater' ? '劇場を検索' : '作品を検索'"
      />
      <button type="submit">検索</button>
    </form>

    <div v-if="searchType === 'person' && popularPeople.length" class="person-cloud mt-3">
      <button v-for="person in popularPeople" :key="person.id" class="person-tag" :style="personTagStyle(person)" @click="searchByPerson(person.name)">
        {{ person.name }}
      </button>
    </div>

    <div v-if="searchType === 'person' && !query.trim()" class="person-prompt">
      <IconUser :size="20" />
      <span>俳優名を選ぶと、出演していた作品が並びます</span>
    </div>

    <AppLoader v-if="searchType !== 'theater' && loading" />
    <section v-else-if="searchType !== 'theater' && !(searchType === 'person' && !query.trim())" class="mt-4">
      <h2 v-if="searchType === 'person' && query.trim()" class="search-result-heading">{{ query }}の出演作</h2>
      <div v-if="works.length" class="work-results">
        <div v-for="work in works" :key="work.id" class="work-result-row">
          <RouterLink :to="`/works/${work.slug}`" class="work-result-main">
            <div class="min-w-0">
              <div class="work-result-title">{{ work.title }}</div>
              <div class="work-result-meta">
                <span v-if="work.theater_name"><IconMapPin :size="12" />{{ work.theater_name }}</span>
                <span v-if="work.start_date"><IconCalendarEvent :size="12" />{{ work.start_date.replaceAll('-', '.') }}</span>
              </div>
            </div>
            <IconChevronRight :size="18" :stroke="1.5" class="result-arrow" />
          </RouterLink>
          <RouterLink
            v-if="auth.isAuthenticated"
            :to="`/works/${work.slug}/edit`"
            class="work-result-edit"
            :aria-label="`${work.title}を編集`"
          ><IconPencil :size="14" /></RouterLink>
        </div>
      </div>

      <div v-else class="search-empty">
        <IconSearch :size="26" :stroke="1.4" />
        <p class="small mb-1">{{ query ? `「${query}」は見つかりませんでした` : '作品がまだありません' }}</p>
        <span class="tiny text-secondary">表記を変えて、もう一度検索してみてください。</span>
      </div>

      <RouterLink
        v-if="auth.isAuthenticated && searchType === 'title' && query.trim()"
        :to="{ path: '/works/new', query: { title: query.trim() } }"
        class="new-work-link"
      >
        <IconPlus :size="14" />探している作品がない場合は、新しく登録
      </RouterLink>
    </section>

    <AppLoader v-if="searchType === 'theater' && theatersLoading" />
    <section v-else-if="searchType === 'theater'" class="theater-results mt-4">
      <RouterLink v-for="theater in theaters" :key="theater.id" :to="`/theaters/${theater.slug}`" class="theater-result-row">
        <div class="theater-result-thumb">
          <img v-if="theaterImage(theater)" :src="theaterImage(theater)" :alt="theater.name" loading="lazy" />
          <div
            v-else
            class="theater-result-placeholder"
            :class="{ 'is-loading': theaterPhotoLoadingSlugs.has(theater.slug) }"
          ><IconTheater :size="23" /></div>
          <span v-if="usesGoogleTheaterImage(theater)" class="theater-google-credit" translate="no">Google</span>
        </div>
        <div class="min-w-0 flex-grow-1">
          <div class="work-result-title">{{ theater.name }}</div>
          <div class="work-result-meta">
            <span v-if="theater.area_name"><IconMapPin :size="12" />{{ theater.area_name }}</span>
            <span v-if="theater.nearest_station">{{ theater.nearest_station }}</span>
          </div>
        </div>
        <IconChevronRight :size="18" class="result-arrow" />
      </RouterLink>
      <div v-if="!theaters.length" class="search-empty">
        <IconTheater :size="26" />
        <p class="small mb-1">{{ query ? `「${query}」に合う劇場は見つかりませんでした` : '劇場がまだありません' }}</p>
      </div>
      <button
        v-if="theaterHasNext"
        type="button"
        class="load-more-theaters"
        :disabled="theatersLoadingMore"
        @click="fetchTheaters({ append: true })"
      >{{ theatersLoadingMore ? '読み込み中…' : 'もっと見る' }}</button>
    </section>
  </div>
</template>

<style scoped>
.search-mode { display: inline-flex; gap: 3px; padding: 3px; border-radius: 10px; background: #18181b; }
.search-mode button { display: inline-flex; align-items: center; gap: 4px; padding: .35rem .7rem; border: 0; border-radius: 8px; background: transparent; color: #71717a; font-size: .72rem; font-weight: 700; }
.search-mode button.active { background: #3f3f46; color: #fff; }
.work-search-form { display: flex; align-items: center; gap: .6rem; padding: .55rem .6rem .55rem .8rem; border: 1px solid rgba(255,255,255,.13); border-radius: 13px; background: #18181b; color: #71717a; }
.work-search-form input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; color: #fff; font-size: .9rem; }
.work-search-form button { padding: .42rem .8rem; border: 0; border-radius: 9px; background: #fff; color: #18181b; font-size: .72rem; font-weight: 800; }
.person-cloud { display: flex; flex-wrap: wrap; gap: .42rem; padding: .9rem; border-radius: 13px; background: radial-gradient(circle at top right, rgba(244,63,94,.09), transparent 45%), rgba(255,255,255,.025); }
.person-tag { padding: .3rem .7rem; border: 1px solid rgba(255,255,255,.1); border-radius: 99px; background: rgba(255,255,255,.06); line-height: 1.15; transition: color .15s, background .15s; }
.person-tag:hover { background: rgba(255,255,255,.1); color: #fff !important; }
.person-prompt { padding: 1.65rem 1rem; display: flex; flex-direction: column; align-items: center; gap: .5rem; color: #52525b; font-size: .68rem; text-align: center; }
.search-result-heading { margin: 0 0 .55rem; color: #a1a1aa; font-size: .72rem; font-weight: 700; }
.work-results { display: flex; flex-direction: column; }
.work-result-row { display: flex; align-items: stretch; border-bottom: 1px solid rgba(255,255,255,.09); }
.work-result-main { display: flex; min-width: 0; flex: 1; align-items: center; justify-content: space-between; gap: 1rem; padding: 1rem .25rem; color: #fff; text-decoration: none; }
.work-result-title { overflow: hidden; font-size: .92rem; font-weight: 750; text-overflow: ellipsis; white-space: nowrap; }
.work-result-meta { display: flex; flex-wrap: wrap; gap: .45rem .8rem; margin-top: .45rem; color: #71717a; font-size: .67rem; }
.work-result-meta span { display: inline-flex; align-items: center; gap: 3px; }
.result-arrow { flex: 0 0 auto; color: #52525b; }
.work-result-edit { display: flex; align-items: center; padding: 0 .6rem; color: #52525b; text-decoration: none; }
.search-empty { padding: 2.5rem 1rem; text-align: center; color: #71717a; }
.new-work-link { display: flex; align-items: center; justify-content: center; gap: 5px; margin-top: 1.25rem; padding: .75rem; border: 1px dashed rgba(244,63,94,.28); border-radius: 12px; color: #fda4af; font-size: .76rem; text-decoration: none; }
.theater-results { border-top: 1px solid rgba(255,255,255,.08); }
.theater-result-row { min-height: 76px; padding: 10px 2px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,.08); color: #fff; text-decoration: none; }
.theater-result-row > .min-w-0 { min-width: 0; }
.theater-result-row:hover { background: rgba(255,255,255,.025); }
.theater-result-thumb { position: relative; width: 72px; height: 54px; flex: 0 0 auto; overflow: hidden; border-radius: 8px; }
.theater-result-thumb img { width: 100%; height: 100%; object-fit: cover; }
.theater-google-credit { position: absolute; right: 3px; bottom: 3px; padding: 1px 3px; border-radius: 3px; background: rgba(0,0,0,.66); color: #fff; font: 500 .44rem/1.25 Roboto, sans-serif; }
.theater-result-placeholder { width: 100%; height: 100%; display: grid; place-items: center; color: rgba(255,255,255,.55); background: radial-gradient(circle at 20% 25%, rgba(244,63,94,.32), transparent 35%), radial-gradient(circle at 82% 75%, rgba(251,191,36,.2), transparent 38%), #202023; }
.theater-result-placeholder.is-loading { position: relative; overflow: hidden; color: rgba(255,255,255,.28); }
.theater-result-placeholder.is-loading::after { content: ''; position: absolute; inset: 0; background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,.09) 47%, transparent 64%); transform: translateX(-100%); animation: theater-photo-loading 1.25s ease-in-out infinite; }
@keyframes theater-photo-loading { to { transform: translateX(100%); } }
.load-more-theaters { display: block; width: 100%; margin: .85rem 0 0; padding: .7rem; border: 1px solid rgba(255,255,255,.12); border-radius: 11px; background: rgba(255,255,255,.035); color: #a1a1aa; font-size: .73rem; font-weight: 700; }
.load-more-theaters:disabled { opacity: .5; }
</style>
