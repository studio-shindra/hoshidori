<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_HERO } from '@/lib/cloudinary'
import { IconMapPin, IconArrowLeft, IconTheater, IconExternalLink } from '@tabler/icons-vue'
import ShopCard from '@/components/ShopCard.vue'

const route = useRoute()
const router = useRouter()
const theater = ref(null)
const theaterPlace = ref(null)
const shops = ref([])
const loading = ref(true)

const tierOrder = { sponsored: 0, recognized: 1, google: 2 }
const sortedShops = computed(() => [...shops.value].sort((a, b) =>
  (tierOrder[a.listing_tier] ?? 9) - (tierOrder[b.listing_tier] ?? 9),
))
const sponsoredShops = computed(() => sortedShops.value.filter((shop) => shop.listing_tier === 'sponsored'))
const recognizedShops = computed(() => sortedShops.value.filter((shop) => shop.listing_tier === 'recognized'))
const googleShops = computed(() => sortedShops.value.filter((shop) => shop.source === 'google_places'))
const ownedHeroImage = computed(() => theater.value?.image_url || theater.value?.image || '')
const heroImage = computed(() => ownedHeroImage.value || theaterPlace.value?.photo_uri || '')
const usesGooglePhoto = computed(() => !ownedHeroImage.value && !!theaterPlace.value?.photo_uri)
const googleMapsUrl = computed(() => theaterPlace.value?.google_maps_uri || (theater.value?.address
  ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(theater.value.address)}`
  : ''))

onMounted(async () => {
  try {
    const slug = route.params.slug
    const [t, s] = await Promise.all([
      api.get(`/api/theaters/${slug}/`),
      api.getFresh(`/api/theaters/${slug}/shops/?include_google=1`).catch(() => []),
    ])
    theater.value = t
    shops.value = s.results || s
    if (!t.image_url && !t.image) {
      api.getFresh(`/api/theaters/${slug}/google-place/`)
        .then((place) => { theaterPlace.value = place })
        .catch(() => {})
    }
  } catch (error) {
    if (error.status === 404) router.replace({ name: 'not-found' })
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
          <img v-if="heroImage" :src="cloudinaryUrl(heroImage, IMG_HERO)" :alt="theater.name" class="w-100 h-100 object-fit-cover" />
          <div v-else class="theater-hero-placeholder">
            <IconTheater :size="42" />
            <span>HOSHIDORI THEATER</span>
          </div>
        </div>
        <button class="btn btn-dark btn-sm position-absolute top-0 start-0 m-3 rounded-circle back-btn" aria-label="戻る" @click="router.back()">
          <IconArrowLeft :size="16" />
        </button>
        <div class="theater-hero-fade"></div>
        <div v-if="usesGooglePhoto" class="google-photo-credit">
          <a :href="theaterPlace.photo_google_maps_uri || theaterPlace.google_maps_uri" target="_blank" rel="noopener noreferrer">Google Maps</a>
          <template v-for="author in theaterPlace.author_attributions" :key="author.display_name">
            <span> · </span><a :href="author.uri || theaterPlace.google_maps_uri" target="_blank" rel="noopener noreferrer">{{ author.display_name }}</a>
          </template>
        </div>
      </div>

      <!-- Info -->
      <div class="px-3 position-relative" style="margin-top: -1.5rem; z-index: 2">
        <h1 class="fs-4 fw-bold mb-1">{{ theater.name }}</h1>
        <div v-if="theater.area_name" class="d-flex align-items-center gap-1 small text-secondary">
          <IconMapPin :size="14" />{{ theater.area_name }}
        </div>
        <div v-if="theater.address" class="small text-secondary mt-1">{{ theater.address }}</div>
        <p v-if="theater.description" class="text-light mt-3 lh-base border-top border-secondary pt-3">{{ theater.description }}</p>

        <a v-if="googleMapsUrl" :href="googleMapsUrl" target="_blank" rel="noopener noreferrer" class="map-link-card mt-3">
          <span class="d-flex align-items-center gap-2"><IconMapPin :size="18" />Google Mapsで場所を見る</span>
          <IconExternalLink :size="16" />
        </a>
      </div>

      <section class="venue-owner-card mx-3 mt-4">
        <div>
          <h2>劇場関係者の方へ</h2>
          <p>公式写真の掲載や、劇場情報の修正をご希望の場合はこちら。</p>
        </div>
        <RouterLink
          :to="{ name: 'contact', query: { category: 'theater', theater: theater.name, source: route.fullPath } }"
        >ご連絡ください →</RouterLink>
      </section>

      <!-- Nearby shops -->
      <section v-if="sortedShops.length" class="px-3 mt-4 mb-5">
        <h3 class="df-center fw-bold mb-3">この劇場の近くのお店</h3>
        <div v-if="sponsoredShops.length" class="d-flex flex-column gap-3 mb-3">
          <ShopCard v-for="shop in sponsoredShops" :key="shop.id" :shop="shop" />
        </div>
        <div v-if="recognizedShops.length" class="d-flex flex-column gap-3 mb-3">
          <ShopCard v-for="shop in recognizedShops" :key="shop.id" :shop="shop" />
        </div>
        <div v-if="googleShops.length" class="google-shop-list">
          <div class="d-flex justify-content-end mb-1">
            <a :href="googleMapsUrl" target="_blank" rel="noopener noreferrer" class="google-attribution" translate="no">
              Google Mapsで見る<IconExternalLink :size="12" />
            </a>
          </div>
          <ShopCard v-for="shop in googleShops" :key="shop.id" :shop="shop" />
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
.theater-hero-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .55rem;
  color: rgba(255,255,255,.64);
  background:
    radial-gradient(circle at 18% 24%, rgba(244,63,94,.3), transparent 32%),
    radial-gradient(circle at 82% 68%, rgba(251,191,36,.18), transparent 34%),
    #202023;
}
.theater-hero-placeholder span { font-size: .58rem; letter-spacing: .18em; }
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
.theater-hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 8rem;
  background: linear-gradient(transparent, #0a0a0b 70%);
}
.google-photo-credit { position: absolute; right: 10px; bottom: 26px; z-index: 2; padding: 3px 6px; border-radius: 5px; background: rgba(0,0,0,.62); color: #d4d4d8; font: 500 .56rem/1.3 Roboto, sans-serif; }
.google-photo-credit a { color: #fff; text-decoration: none; }
.google-attribution { display: inline-flex; align-items: center; gap: 4px; color: #a1a1aa; font-family: Roboto, sans-serif; font-size: .72rem; text-decoration: none; white-space: nowrap; }
.google-shop-list { margin-top: .2rem; }
.venue-owner-card { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 14px 15px; border: 1px solid rgba(255,255,255,.09); border-radius: 12px; background: #18181b; }
.venue-owner-card h2 { margin: 0 0 .25rem; font-size: .78rem; font-weight: 800; }
.venue-owner-card p { margin: 0; color: #71717a; font-size: .65rem; line-height: 1.55; }
.venue-owner-card a { flex-shrink: 0; color: #fda4af; font-size: .68rem; font-weight: 700; text-decoration: none; }
.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
</style>
