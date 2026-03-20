<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_THUMB } from '@/lib/cloudinary'
import { IconMapPin, IconSearch, IconTheater } from '@tabler/icons-vue'

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
  <div class="pt-4">
    <h2 class="fs-5 fw-bold mb-3 fs-2">Theater List</h2>

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
    <div v-else class="grid-wrapper">
      <RouterLink
        v-for="t in theaters"
        :key="t.id"
        :to="`/theaters/${t.slug}`"
        class="theater-card text-decoration-none position-relative"
      >
        <img v-if="t.image" :src="cloudinaryUrl(t.image, IMG_THUMB)" :alt="t.name" class="theater-card-img" loading="lazy" />
        <div v-else class="theater-card-img theater-card-placeholder">
          <IconTheater :size="32" class="text-secondary" />
        </div>
        <div class="theater-card-overlay">
          <div class="fw-bold small text-white">{{ t.name }}</div>
          <div v-if="t.area_name" class="d-flex align-items-center gap-1 tiny text-white mt-1">
            <IconMapPin :size="11" />{{ t.area_name }}
          </div>
        </div>
      </RouterLink>
    </div>
    <p v-if="!loading && !theaters.length" class="text-secondary text-center mt-4">
      {{ query ? '該当する劇場がありません' : '劇場がまだありません' }}
    </p>
  </div>
</template>

<style scoped>
.theater-card {
  display: block;
  border-radius: 0.5rem;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  position: relative;
}

.theater-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.theater-card-placeholder {
  background: #27272a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theater-card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.75rem;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.5) 60%, transparent 100%);
}
</style>
