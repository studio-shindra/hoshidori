<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_HERO } from '@/lib/cloudinary'
import { IconMapPin, IconArrowLeft, IconTheater } from '@tabler/icons-vue'
import ShopCard from '@/components/ShopCard.vue'

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
    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="theater">
      <!-- Hero -->
      <div class="position-relative">
        <div class="theater-hero">
          <img v-if="theater.image" :src="cloudinaryUrl(theater.image, IMG_HERO)" :alt="theater.name" class="w-100 h-100 object-fit-cover" />
          <div v-else class="w-100 h-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #27272a, #3f3f46)">
            <IconTheater :size="48" class="text-secondary" />
          </div>
        </div>
        <button class="btn btn-dark btn-sm position-absolute top-0 start-0 m-3 rounded-circle back-btn" @click="router.back()">
          <IconArrowLeft :size="16" />
        </button>
        <div class="theater-hero-fade"></div>
      </div>

      <!-- Info -->
      <div class="px-3 position-relative" style="margin-top: -1.5rem; z-index: 2">
        <h2 class="fs-4 fw-bold mb-1">{{ theater.name }}</h2>
        <div v-if="theater.area_name" class="d-flex align-items-center gap-1 small text-secondary">
          <IconMapPin :size="14" />{{ theater.area_name }}
        </div>
        <div v-if="theater.address" class="small text-secondary mt-1">{{ theater.address }}</div>
        <p v-if="theater.description" class="text-light mt-3 lh-base border-top border-secondary pt-3">{{ theater.description }}</p>

        <!-- Google Map -->
        <div v-if="theater.address" class="mt-3 overflow-hidden">
          <iframe
            :src="`https://maps.google.com/maps?q=${encodeURIComponent(theater.address)}&output=embed&z=16`"
            width="100%"
            height="200"
            style="border:0"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>
      </div>

      <!-- Nearby shops -->
      <section v-if="sortedShops.length" class="px-3 mt-4 mb-5">
        <h3 class="df-center fw-bold mb-3">この劇場の近くのお店</h3>
        <div class="d-flex flex-column gap-3">
          <ShopCard v-for="s in sortedShops" :key="s.id" :shop="s" />
        </div>
        <RouterLink
          :to="{ path: '/shops', query: { theater: route.params.slug } }"
          class="btn btn-dark btn-sm text-secondary w-100 mt-3"
        >
          この劇場の近くの店をもっと見る →
        </RouterLink>
      </section>
    </template>
  </div>
</template>

<style scoped>
.theater-hero {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.theater-hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 8rem;
  background: linear-gradient(transparent, #0a0a0b 70%);
}
.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
</style>
