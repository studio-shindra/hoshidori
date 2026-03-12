<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { IconMask, IconSearch, IconPlus } from '@tabler/icons-vue'

const auth = useAuthStore()
const works = ref([])
const loading = ref(true)
const query = ref('')

async function fetchWorks() {
  loading.value = true
  try {
    const q = query.value.trim()
    const url = q ? `/api/works/?q=${encodeURIComponent(q)}` : '/api/works/'
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
</script>

<template>
  <div class="px-3 pt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="fs-5 fw-bold mb-0">作品一覧</h2>
      <RouterLink v-if="auth.isAuthenticated" to="/works/new" class="btn btn-outline-secondary btn-sm">
        <IconPlus :size="14" class="me-1" />作品登録
      </RouterLink>
    </div>

    <!-- Search -->
    <form @submit.prevent="onSearch" class="d-flex gap-2 mb-3">
      <input
        v-model="query"
        type="text"
        placeholder="作品名で検索"
        class="form-control bg-dark border-secondary text-light form-control-sm"
      />
      <button type="submit" class="btn btn-dark btn-sm px-3">
        <IconSearch :size="16" />
      </button>
    </form>

    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <div v-else class="d-flex flex-column gap-2">
      <RouterLink
        v-for="w in works"
        :key="w.id"
        :to="`/works/${w.slug}`"
        class="card bg-dark border-0 p-3 text-decoration-none"
      >
        <div class="d-flex gap-3">
          <div v-if="w.selected_poster_image_url" class="thumb overflow-hidden rounded-2">
            <img :src="w.selected_poster_image_url" class="w-100 h-100 object-fit-cover" />
          </div>
          <div v-else class="thumb poster-empty d-flex align-items-center justify-content-center">
            <IconMask :size="18" class="text-secondary" />
          </div>
          <div class="flex-grow-1 min-w-0">
            <div class="fw-medium small text-light text-truncate">{{ w.title || w.name }}</div>
            <div v-if="w.theater_name" class="tiny text-secondary mt-1">{{ w.theater_name }}</div>
          </div>
        </div>
      </RouterLink>
    </div>
    <p v-if="!loading && !works.length" class="text-secondary text-center mt-4">
      {{ query ? '該当する作品がありません' : '作品がまだありません' }}
    </p>
  </div>
</template>

<style scoped>
.thumb {
  width: 56px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 8px;
}
</style>
