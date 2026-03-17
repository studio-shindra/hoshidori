<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconSearch, IconCoffee } from '@tabler/icons-vue'
import ShopCard from '@/components/ShopCard.vue'

const route = useRoute()
const router = useRouter()
const shops = ref([])
const loading = ref(true)
const keyword = ref('')
const activeCategory = ref('')

const categories = [
  { label: 'すべて', value: '' },
  { label: 'カフェ', value: 'カフェ' },
  { label: '居酒屋', value: '居酒屋' },
  { label: 'バー', value: 'バー' },
]

function buildQuery() {
  const params = new URLSearchParams()
  if (keyword.value) params.set('q', keyword.value)
  if (activeCategory.value) params.set('category', activeCategory.value)
  if (route.query.theater) params.set('theater', route.query.theater)
  return params.toString() ? `?${params}` : ''
}

async function search() {
  loading.value = true
  try {
    const data = await api.get(`/api/shops/${buildQuery()}`)
    shops.value = data.results || data
  } catch {
    shops.value = []
  } finally {
    loading.value = false
  }
}

function onSubmit() {
  search()
}

function selectCategory(val) {
  activeCategory.value = val
  search()
}

onMounted(() => {
  keyword.value = route.query.q || ''
  activeCategory.value = route.query.category || ''
  search()
})
</script>

<template>
  <div class="pb-4">
    <h1 class="d-flex align-items-center gap-2 fw-bold fs-3 mb-3">
      <IconCoffee :size="22" />
      店を探す
    </h1>

    <!-- Search bar -->
    <form class="d-flex gap-2 mb-3" @submit.prevent="onSubmit">
      <input
        v-model="keyword"
        type="text"
        class="form-control bg-dark text-white border-secondary"
        placeholder="店名で探す"
      />
      <button type="submit" class="btn btn-outline-light flex-shrink-0">
        <IconSearch :size="18" />
      </button>
    </form>

    <!-- Category pills -->
    <div class="d-flex gap-2 mb-4 overflow-auto scroll-hide">
      <button
        v-for="cat in categories"
        :key="cat.value"
        class="btn btn-sm rounded-pill flex-shrink-0"
        :class="activeCategory === cat.value ? 'btn-light' : 'btn-outline-secondary'"
        @click="selectCategory(cat.value)"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Theater filter notice -->
    <div v-if="route.query.theater" class="mb-3">
      <span class="badge bg-secondary">{{ route.query.theater }} の近くの店</span>
      <RouterLink :to="{ path: '/shops' }" class="ms-2 small text-secondary">クリア</RouterLink>
    </div>

    <!-- Results -->
    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else>
      <div v-if="shops.length" class="d-flex flex-column gap-3">
        <ShopCard v-for="shop in shops" :key="shop.id" :shop="shop" />
      </div>
      <div v-else class="text-center py-5">
        <IconCoffee :size="40" class="text-secondary mb-2" />
        <p class="text-secondary">条件に合う店舗が見つかりませんでした</p>
      </div>
    </template>
  </div>
</template>
