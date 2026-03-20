<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_HERO } from '@/lib/cloudinary'
import {
  IconArrowLeft, IconExternalLink, IconTicket,
  IconBrandInstagram, IconWorld, IconPhone, IconToolsKitchen2, IconMap,
} from '@tabler/icons-vue'
import CouponDetailModal from '@/components/CouponDetailModal.vue'

const route = useRoute()
const router = useRouter()
const shop = ref(null)
const coupons = ref([])
const selectedCoupon = ref(null)
const loading = ref(true)

// per-coupon feedback
const couponStates = ref({})

onMounted(async () => {
  try {
    const slug = route.params.slug
    shop.value = await api.get(`/api/shops/${slug}/`)
    api.post(`/api/shops/${slug}/click/`).catch(() => {})
    try {
      const data = await api.get(`/api/shops/${slug}/coupons/`)
      coupons.value = Array.isArray(data) ? data : data.results || []
    } catch {
      /* empty */
    }
  } finally {
    loading.value = false
  }
})

async function useCoupon(coupon) {
  const state = { loading: true, msg: '', type: '', cooldown: null }
  couponStates.value[coupon.id] = state
  try {
    const result = await api.post(`/api/coupons/${coupon.id}/use/`, { performance: null })
    state.msg = 'クーポンを利用しました！'
    state.type = 'success'
    if (result.used_at) {
      const d = new Date(result.used_at)
      state.msg += ` (${d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })})`
    }
  } catch (e) {
    if (e.status === 429) {
      state.type = 'cooldown'
      const remaining = e.data?.cooldown_minutes_remaining
      if (remaining) {
        state.msg = `短時間での再利用はできません（残り約${Math.ceil(remaining)}分）`
        state.cooldown = Math.ceil(remaining)
      } else {
        state.msg = '短時間での再利用はできません'
      }
    } else if (e.status === 401) {
      state.msg = 'ログインが必要です'
      state.type = 'error'
    } else {
      state.msg = 'エラーが発生しました'
      state.type = 'error'
    }
  } finally {
    state.loading = false
  }
}
</script>

<template>
  <div class="pb-5">
    <!-- <header class="d-flex align-items-center gap-2 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">お店</h1>
    </header> -->

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="shop">
      <!-- Hero image -->
      <div class="shop-hero position-relative">
        <img v-if="shop.image_src" :src="cloudinaryUrl(shop.image_src, IMG_HERO)" :alt="shop.name" class="w-100 h-100 object-fit-cover" />
        <div v-else class="w-100 h-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #27272a, #3f3f46)">
          <IconToolsKitchen2 :size="48" class="text-secondary" />
        </div>
        <div class="shop-hero-fade"></div>
      </div>

      <div class="position-relative" style="margin-top: -1.5rem; z-index: 2">
        <h2 class="fs-3 fw-bold mb-1">{{ shop.name }}</h2>

        <!-- SNS icons -->
        <div class="d-flex align-items-center gap-3 mt-2">
          <component :is="shop.website_url ? 'a' : 'span'" :href="shop.website_url || undefined" :target="shop.website_url ? '_blank' : undefined" class="sns-circle" :style="{ background: shop.website_url ? '#a1a1aa' : '#3f3f46' }">
            <IconWorld :size="20" />
          </component>
          <component :is="shop.instagram_url ? 'a' : 'span'" :href="shop.instagram_url || undefined" :target="shop.instagram_url ? '_blank' : undefined" class="sns-circle" :style="{ background: shop.instagram_url ? '#E1306C' : '#3f3f46' }">
            <IconBrandInstagram :size="20" />
          </component>
          <component :is="shop.tabelog_url ? 'a' : 'span'" :href="shop.tabelog_url || undefined" :target="shop.tabelog_url ? '_blank' : undefined" class="sns-circle" :style="{ background: shop.tabelog_url ? '#f59e0b' : '#3f3f46' }">
            <IconToolsKitchen2 :size="20" />
          </component>
          <component :is="shop.google_map_url ? 'a' : 'span'" :href="shop.google_map_url || undefined" :target="shop.google_map_url ? '_blank' : undefined" class="sns-circle" :style="{ background: shop.google_map_url ? '#34d399' : '#3f3f46' }">
            <IconMap :size="20" />
          </component>
        </div>

        <div v-if="shop.category" class="small text-secondary mt-2">{{ shop.category }}</div>
        <div v-if="shop.address" class="small text-white mt-1">{{ shop.address }}</div>
        <p v-if="shop.description" class="text-light border-top border-secondary mt-3 pt-3 lh-base">{{ shop.description }}</p>

        <!-- Google Map embed -->
        <div v-if="shop.address" class="mt-3 overflow-hidden">
          <iframe
            :src="`https://maps.google.com/maps?q=${encodeURIComponent(shop.address)}&output=embed&z=16`"
            width="100%"
            height="200"
            style="border:0"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>

        <!-- Action buttons -->
        <div class="d-flex gap-2 mt-3">
          <component :is="shop.phone_number ? 'a' : 'span'" :href="shop.phone_number ? `tel:${shop.phone_number}` : undefined" class="btn flex-fill d-flex align-items-center justify-content-center gap-1" :class="shop.phone_number ? 'btn-dark text-white' : 'btn-dark text-secondary opacity-50'" :style="{ pointerEvents: shop.phone_number ? 'auto' : 'none' }">
            <IconPhone :size="16" />電話する
          </component>
          <component :is="shop.tabelog_url ? 'a' : 'span'" :href="shop.tabelog_url || undefined" :target="shop.tabelog_url ? '_blank' : undefined" class="btn flex-fill d-flex align-items-center justify-content-center gap-1 fw-bold" :class="shop.tabelog_url ? 'text-white' : 'btn-dark text-secondary opacity-50'" :style="{ background: shop.tabelog_url ? '#f59e0b' : undefined, pointerEvents: shop.tabelog_url ? 'auto' : 'none' }">
            <IconExternalLink :size="16" />詳細を見る
          </component>
        </div>

        <!-- Coupons -->
        <section v-if="coupons.length" class="mt-4 mb-5">
          <h3 class="df-center fw-semibold text-white mb-3">
            <IconTicket :size="28" class="me-1" />クーポン
          </h3>
          <div class="d-flex flex-column gap-2">
            <div
              v-for="c in coupons"
              :key="c.id"
              class="coupon-card"
            >
              <div class="d-flex align-items-center gap-2">
                <IconTicket :size="16" class="color-rose flex-shrink-0" />
                <div class="flex-grow-1 min-w-0" role="button" @click="selectedCoupon = c">
                  <div class="fw-bold">{{ c.title }}</div>
                  <div v-if="c.discount_text" class="small color-rose">{{ c.discount_text }}</div>
                </div>
                <button class="btn btn-sm btn-primary-rose flex-shrink-0" @click="selectedCoupon = c">使う</button>
              </div>
              <div v-if="couponStates[c.id]?.msg" class="mt-2 small" :class="{ 'color-green': couponStates[c.id].type === 'success', 'color-amber': couponStates[c.id].type === 'cooldown', 'text-danger': couponStates[c.id].type === 'error' }">
                {{ couponStates[c.id].msg }}
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Coupon modal -->
      <CouponDetailModal
        :coupon="selectedCoupon"
        :shop-name="shop.name"
        @close="selectedCoupon = null"
        @use="useCoupon($event); selectedCoupon = null"
      />
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
.coupon-card {
  background: white;
  border: 2px dashed #e11d48;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  width: 100%;
  cursor: pointer;
  color: #e11d48;

  &:hover,
  &:active,
  &:focus {
    background: white;
  }
}
</style>
