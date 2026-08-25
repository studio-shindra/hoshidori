<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_HERO } from '@/lib/cloudinary'
import {
  IconExternalLink, IconSparkles,
  IconArrowLeft, IconBrandInstagram, IconWorld, IconPhone, IconToolsKitchen2, IconMap,
  IconBuildingStore, IconBooks, IconShirt, IconCoffee,
} from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()
const shop = ref(null)
const loading = ref(true)
const googleMapsUrl = computed(() => {
  if (!shop.value) return ''
  if (shop.value.google_map_url) return shop.value.google_map_url
  return shop.value.address
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(shop.value.address)}`
    : ''
})
const detailUrl = computed(() => shop.value?.tabelog_url || shop.value?.website_url || '')
const categoryIcon = computed(() => {
  const category = shop.value?.category || ''
  if (/書店|本屋|古本/.test(category)) return IconBooks
  if (/古着|衣料|アパレル/.test(category)) return IconShirt
  if (/カフェ|喫茶|コーヒー|珈琲/.test(category)) return IconCoffee
  if (/飲食|居酒屋|バー|料理|ビストロ|カレー/.test(category)) return IconToolsKitchen2
  return IconBuildingStore
})

onMounted(async () => {
  try {
    const slug = route.params.slug
    shop.value = await api.get(`/api/shops/${slug}/`)
    api.post(`/api/shops/${slug}/click/`).catch(() => {})
  } catch (error) {
    if (error.status === 404) router.replace({ name: 'not-found' })
  } finally {
    loading.value = false
  }
})

</script>

<template>
  <div class="pb-5">
    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="shop">
      <!-- Hero image -->
      <div class="shop-hero position-relative">
        <img v-if="shop.image_src" :src="cloudinaryUrl(shop.image_src, IMG_HERO)" :alt="shop.name" class="w-100 h-100 object-fit-cover" />
        <div v-else class="w-100 h-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #27272a, #3f3f46)">
          <component :is="categoryIcon" :size="48" class="text-secondary" />
        </div>
        <div class="shop-hero-fade"></div>
        <button class="btn btn-dark btn-sm position-absolute top-0 start-0 m-3 rounded-circle back-btn" aria-label="戻る" @click="router.back()">
          <IconArrowLeft :size="16" />
        </button>
      </div>

      <div class="position-relative" style="margin-top: -1.5rem; z-index: 2">
        <h1 class="fs-3 fw-bold mb-1">{{ shop.name }}</h1>

        <!-- SNS icons -->
        <div class="d-flex align-items-center gap-3 mt-2">
          <component :is="shop.website_url ? 'a' : 'span'" :href="shop.website_url || undefined" :target="shop.website_url ? '_blank' : undefined" :rel="shop.website_url ? 'noopener noreferrer' : undefined" aria-label="公式サイト" class="sns-circle" :style="{ background: shop.website_url ? '#a1a1aa' : '#3f3f46' }">
            <IconWorld :size="20" />
          </component>
          <component :is="shop.instagram_url ? 'a' : 'span'" :href="shop.instagram_url || undefined" :target="shop.instagram_url ? '_blank' : undefined" :rel="shop.instagram_url ? 'noopener noreferrer' : undefined" aria-label="Instagram" class="sns-circle" :style="{ background: shop.instagram_url ? '#E1306C' : '#3f3f46' }">
            <IconBrandInstagram :size="20" />
          </component>
          <component :is="shop.tabelog_url ? 'a' : 'span'" :href="shop.tabelog_url || undefined" :target="shop.tabelog_url ? '_blank' : undefined" :rel="shop.tabelog_url ? 'noopener noreferrer' : undefined" aria-label="店舗詳細" class="sns-circle" :style="{ background: shop.tabelog_url ? '#f59e0b' : '#3f3f46' }">
            <IconBuildingStore :size="20" />
          </component>
          <component :is="shop.google_map_url ? 'a' : 'span'" :href="shop.google_map_url || undefined" :target="shop.google_map_url ? '_blank' : undefined" :rel="shop.google_map_url ? 'noopener noreferrer' : undefined" aria-label="Google Maps" class="sns-circle" :style="{ background: shop.google_map_url ? '#34d399' : '#3f3f46' }">
            <IconMap :size="20" />
          </component>
        </div>

        <div v-if="shop.category" class="small text-secondary mt-2">{{ shop.category }}</div>
        <div v-if="shop.address" class="small text-white mt-1">{{ shop.address }}</div>
        <p v-if="shop.description" class="text-light border-top border-secondary mt-3 pt-3 lh-base">{{ shop.description }}</p>

        <a v-if="googleMapsUrl" :href="googleMapsUrl" target="_blank" rel="noopener noreferrer" class="map-link-card mt-3">
          <span class="d-flex align-items-center gap-2"><IconMap :size="18" />Google Mapsで場所を見る</span>
          <IconExternalLink :size="16" />
        </a>

        <!-- Action buttons -->
        <div class="d-flex gap-2 mt-3">
          <component :is="shop.phone_number ? 'a' : 'span'" :href="shop.phone_number ? `tel:${shop.phone_number}` : undefined" class="btn flex-fill d-flex align-items-center justify-content-center gap-1" :class="shop.phone_number ? 'btn-dark text-white' : 'btn-dark text-secondary opacity-50'" :style="{ pointerEvents: shop.phone_number ? 'auto' : 'none' }">
            <IconPhone :size="16" />{{ shop.phone_number ? '電話する' : '電話情報なし' }}
          </component>
          <component :is="detailUrl ? 'a' : 'span'" :href="detailUrl || undefined" :target="detailUrl ? '_blank' : undefined" class="btn flex-fill d-flex align-items-center justify-content-center gap-1 fw-bold" :class="detailUrl ? 'text-white' : 'btn-dark text-secondary opacity-50'" :style="{ background: detailUrl ? '#f59e0b' : undefined, pointerEvents: detailUrl ? 'auto' : 'none' }">
            <IconExternalLink :size="16" />{{ detailUrl ? '詳細を見る' : '詳細情報なし' }}
          </component>
        </div>

        <section v-if="shop.benefit_text" class="benefit-card mt-4 mb-5">
          <div class="d-flex align-items-start gap-2">
            <IconSparkles :size="18" class="color-rose flex-shrink-0 mt-1" />
            <div>
              <h3 class="small fw-bold mb-1">観劇客へのご案内</h3>
              <p class="small text-light mb-0">{{ shop.benefit_text }}</p>
              <p class="tiny text-secondary mt-2 mb-0">内容や利用方法は店舗でご確認ください。</p>
            </div>
          </div>
        </section>
      </div>

    </template>
  </div>
</template>

<style scoped>
.shop-hero {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.shop-hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6rem;
  background: linear-gradient(transparent, #0a0a0b 70%);
}
.back-btn { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; opacity: .82; }
.sns-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  text-decoration: none;
  transition: opacity 0.15s;

  &:hover {
    opacity: 0.85;
  }
}
.map-link-card {
  min-height: 58px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 12px;
  color: #e4e4e7;
  background: #18181b;
  font-size: .78rem;
  font-weight: 600;
  text-decoration: none;
}
.map-link-card:hover { color: #fff; background: #202023; }
.benefit-card {
  background: rgba(244, 63, 94, 0.08);
  border: 1px solid rgba(244, 63, 94, 0.24);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  width: 100%;
}
</style>
