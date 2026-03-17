<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { IconSearch, IconPlus, IconTheater, IconMasksTheater, IconUser } from '@tabler/icons-vue'
import PosterImage from '@/components/PosterImage.vue'
import AppLoader from '@/components/AppLoader.vue'

const auth = useAuthStore()
const works = ref([])
const loading = ref(true)
const query = ref('')
const searchType = ref('title') // 'title' | 'person'

async function fetchWorks() {
  loading.value = true
  try {
    const q = query.value.trim()
    let url = '/api/works/'
    if (q) {
      url = searchType.value === 'person'
        ? `/api/works/?person=${encodeURIComponent(q)}`
        : `/api/works/?q=${encodeURIComponent(q)}`
    }
    const data = await api.get(url)
    works.value = data.results || data
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
}

onMounted(fetchWorks)

function onSearch() {
  fetchWorks()
}

function setSearchType(type) {
  searchType.value = type
  if (query.value.trim()) fetchWorks()
}
</script>

<template>
  <div class="pt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="fw-bold mb-0 fs-2">Works</h2>
      <RouterLink v-if="auth.isAuthenticated" to="/works/new" class="btn btn-outline-secondary btn-sm">
        <IconPlus :size="14" class="me-1" />作品登録
      </RouterLink>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <div class="d-flex gap-1 mb-2">
        <button
          class="btn btn-sm fw-medium"
          :class="searchType === 'title' ? 'btn-light text-dark' : 'btn-dark text-secondary'"
          @click="setSearchType('title')"
        >
          <IconMasksTheater :size="13" class="me-1" />作品名
        </button>
        <button
          class="btn btn-sm fw-medium"
          :class="searchType === 'person' ? 'btn-light text-dark' : 'btn-dark text-secondary'"
          @click="setSearchType('person')"
        >
          <IconUser :size="13" class="me-1" />俳優名
        </button>
      </div>
      <form @submit.prevent="onSearch" class="d-flex gap-2">
        <input
          v-model="query"
          type="text"
          :placeholder="searchType === 'person' ? '俳優名で検索' : '作品名で検索'"
          class="form-control bg-dark border-secondary text-light form-control-sm"
        />
        <button type="submit" class="btn btn-dark btn-sm px-3">
          <IconSearch :size="16" />
        </button>
      </form>
    </div>

    <AppLoader v-if="loading" />
    <div v-else class="grid-wrapper">
      <RouterLink
        v-for="w in works"
        :key="w.id"
        :to="`/works/${w.slug}`"
        class="position-relative d-block text-decoration-none rounded-2 overflow-hidden"
      >
        <PosterImage :src="w.selected_poster_image_url" :alt="w.title" :work-slug="w.slug" />
        <div class="ab-top text-white">
          <div v-if="w.theater_name" class="d-flex align-items-center gap-1 label-xs">
            <IconTheater :size="10" />{{ w.theater_name }}
          </div>
          <div v-if="w.start_date" class="label-xs">{{ w.start_date }}</div>
        </div>
        <div class="ab-bottom dark-gradient text-white">
          <div class="small fw-bold text-truncate">{{ w.title }}</div>
        </div>
      </RouterLink>
    </div>
    <p v-if="!loading && !works.length" class="text-secondary text-center mt-4">
      {{ query ? (searchType === 'person' ? `「${query}」が出演する作品はありません` : '該当する作品がありません') : '作品がまだありません' }}
    </p>
  </div>
</template>

<style scoped>
.grid-works {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}
.label-xs {
  font-size: 0.6rem;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
