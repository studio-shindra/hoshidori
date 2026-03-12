<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { IconMapPin, IconSearch } from '@tabler/icons-vue'

const theaters = ref([])
const loading = ref(true)
const query = ref('')

async function fetchTheaters() {
  loading.value = true
  try {
    const q = query.value.trim()
    const url = q ? `/api/theaters/?q=${encodeURIComponent(q)}` : '/api/theaters/'
    const data = await api.get(url)
    theaters.value = data.results || data
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
}

onMounted(fetchTheaters)

function onSearch() {
  fetchTheaters()
}
</script>

<template>
  <div class="px-3 pt-4">
    <h2 class="fs-5 fw-bold mb-3">劇場一覧</h2>

    <!-- Search -->
    <form @submit.prevent="onSearch" class="d-flex gap-2 mb-3">
      <input
        v-model="query"
        type="text"
        placeholder="劇場名で検索"
        class="form-control bg-dark border-secondary text-light form-control-sm"
      />
      <button type="submit" class="btn btn-dark btn-sm px-3">
        <IconSearch :size="16" />
      </button>
    </form>

    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <div v-else class="d-flex flex-column gap-2">
      <RouterLink
        v-for="t in theaters"
        :key="t.id"
        :to="`/theaters/${t.slug}`"
        class="card bg-dark border-0 p-3 text-decoration-none"
      >
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-medium small text-light">{{ t.name }}</div>
            <div v-if="t.area_name" class="tiny text-secondary mt-1">
              <IconMapPin :size="12" class="me-1" />{{ t.area_name }}
            </div>
          </div>
        </div>
      </RouterLink>
    </div>
    <p v-if="!loading && !theaters.length" class="text-secondary text-center mt-4">
      {{ query ? '該当する劇場がありません' : '劇場がまだありません' }}
    </p>
  </div>
</template>
