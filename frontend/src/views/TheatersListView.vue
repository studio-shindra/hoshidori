<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_THUMB } from '@/lib/cloudinary'
import { IconChevronRight, IconMapPin, IconSearch, IconTheater } from '@tabler/icons-vue'

const theaters = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const query = ref('')
const page = ref(1)
const hasNext = ref(false)

async function fetchTheaters({ append = false } = {}) {
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const q = query.value.trim()
    const nextPage = append ? page.value + 1 : 1
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (nextPage > 1) params.set('page', String(nextPage))
    const data = await api.getFresh(`/api/theaters/?${params.toString()}`)
    const results = data.results || data
    theaters.value = append ? [...theaters.value, ...results] : results
    page.value = nextPage
    hasNext.value = Boolean(data.next)
  } catch {
    if (!append) theaters.value = []
  } finally {
    if (append) loadingMore.value = false
    else loading.value = false
  }
}

onMounted(fetchTheaters)

function onSearch() {
  fetchTheaters()
}
</script>

<template>
  <div class="pt-4">
    <h1 class="fs-3 fw-bold mb-3">劇場を探す</h1>

    <!-- Search -->
    <form @submit.prevent="onSearch" class="d-flex gap-2 mb-3">
      <input
        v-model="query"
        type="text"
        placeholder="劇場名で検索"
        class="form-control bg-dark border-secondary text-light form-control-sm"
      />
      <button type="submit" class="btn btn-dark btn-sm px-3" aria-label="劇場を検索">
        <IconSearch :size="16" />
      </button>
    </form>

    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <div v-else class="theater-list">
      <RouterLink
        v-for="t in theaters"
        :key="t.id"
        :to="`/theaters/${t.slug}`"
        class="theater-row text-decoration-none"
      >
        <div class="theater-thumb">
          <img v-if="t.image" :src="cloudinaryUrl(t.image, IMG_THUMB)" :alt="t.name" loading="lazy" />
          <div v-else class="theater-placeholder">
            <IconTheater :size="24" />
          </div>
        </div>
        <div class="min-w-0 flex-grow-1">
          <div class="fw-bold small text-white text-truncate">{{ t.name }}</div>
          <div v-if="t.area_name" class="d-flex align-items-center gap-1 tiny text-secondary mt-1">
            <IconMapPin :size="11" />{{ t.area_name }}
          </div>
        </div>
        <IconChevronRight :size="17" class="text-secondary flex-shrink-0" />
      </RouterLink>
    </div>
    <p v-if="!loading && !theaters.length" class="text-secondary text-center mt-4">
      {{ query ? '該当する劇場がありません' : '劇場がまだありません' }}
    </p>
    <button
      v-if="!loading && hasNext"
      type="button"
      class="load-more"
      :disabled="loadingMore"
      @click="fetchTheaters({ append: true })"
    >{{ loadingMore ? '読み込み中…' : 'もっと見る' }}</button>
  </div>
</template>

<style scoped>
.theater-list {
  border-top: 1px solid rgba(255,255,255,.08);
}
.theater-row {
  min-height: 76px;
  padding: 10px 2px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.theater-row > .min-w-0 { min-width: 0; }
.theater-row:hover { background: rgba(255,255,255,.025); }
.theater-thumb {
  width: 72px;
  height: 54px;
  flex: 0 0 auto;
  overflow: hidden;
  border-radius: 8px;
}
.theater-thumb img { width: 100%; height: 100%; object-fit: cover; }
.theater-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: rgba(255,255,255,.55);
  background:
    radial-gradient(circle at 20% 25%, rgba(244,63,94,.32), transparent 35%),
    radial-gradient(circle at 82% 75%, rgba(251,191,36,.2), transparent 38%),
    #202023;
}
.load-more {
  width: 100%; margin-top: .85rem; padding: .7rem;
  border: 1px solid rgba(255,255,255,.12); border-radius: 11px;
  background: rgba(255,255,255,.035); color: #a1a1aa;
  font-size: .73rem; font-weight: 700;
}
.load-more:disabled { opacity: .5; }
</style>
