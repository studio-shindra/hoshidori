<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconMapPin, IconArrowLeft } from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()
const theater = ref(null)
const shops = ref([])
const loading = ref(true)

const sortedShops = computed(() =>
  [...shops.value].sort((a, b) => (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0)),
)

onMounted(async () => {
  try {
    const slug = route.params.slug
    const [t, s] = await Promise.all([
      api.get(`/api/theaters/${slug}/`),
      api.get(`/api/theaters/${slug}/shops/`).catch(() => []),
    ])
    theater.value = t
    shops.value = s.results || s
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <header class="d-flex align-items-center gap-2 px-3 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">劇場</h1>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="theater">
      <div class="px-3 mb-4">
        <h2 class="fs-5 fw-bold mb-1">{{ theater.name }}</h2>
        <div v-if="theater.area" class="small text-secondary">
          <IconMapPin :size="14" class="me-1" />{{ theater.area }}
        </div>
        <div v-if="theater.address" class="tiny text-secondary mt-1">{{ theater.address }}</div>
        <p v-if="theater.description" class="small text-light mt-3 lh-base">{{ theater.description }}</p>
      </div>

      <!-- Shop cards (Retty style) -->
      <section v-if="sortedShops.length" class="px-3 mb-5">
        <h3 class="small fw-semibold text-secondary mb-3">この劇場の近くの店</h3>
        <div class="d-flex flex-column gap-3">
          <RouterLink
            v-for="s in sortedShops"
            :key="s.id"
            :to="`/shops/${s.slug}`"
            class="card border-0 p-0 overflow-hidden text-decoration-none"
            :class="s.is_featured ? 'shop-featured' : 'bg-dark'"
          >
            <div class="position-relative">
              <div class="shop-img" :class="s.is_featured ? 'shop-img-featured' : ''"></div>
              <span v-if="s.is_featured" class="badge badge-featured position-absolute top-0 start-0 m-2">おすすめ</span>
            </div>
            <div class="p-3">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-medium small text-light">{{ s.name }}</div>
                  <div class="tiny text-secondary">
                    {{ s.category || '' }}
                    <span v-if="s.walking_minutes"> · 徒歩{{ s.walking_minutes }}分</span>
                  </div>
                  <div class="tiny text-secondary mt-1">{{ s.description || '' }}</div>
                </div>
                <span v-if="s.benefit_text" class="btn btn-sm btn-coupon flex-shrink-0 ms-2">{{ s.benefit_text }}</span>
              </div>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.shop-img {
  width: 100%;
  height: 100px;
  background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
}
.shop-img-featured {
  height: 120px;
  background: linear-gradient(135deg, #44403c 0%, #57534e 50%, #44403c 100%);
}
.shop-featured {
  background: #1c1917;
  border: 1px solid rgba(245, 158, 11, 0.25);
}
</style>
