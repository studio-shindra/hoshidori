<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { IconArrowLeft, IconExternalLink, IconTicket, IconCheck, IconClock } from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const shop = ref(null)
const coupons = ref([])
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
  <div>
    <header class="d-flex align-items-center gap-2 px-3 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">お店</h1>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="shop">
      <div class="px-3">
        <h2 class="fs-5 fw-bold mb-1">{{ shop.name }}</h2>
        <div v-if="shop.category" class="small text-secondary">{{ shop.category }}</div>
        <div v-if="shop.address" class="tiny text-secondary mt-1">{{ shop.address }}</div>
        <p v-if="shop.description" class="small text-light mt-3 lh-base">{{ shop.description }}</p>

        <!-- Benefit -->
        <div v-if="shop.benefit_text" class="card border-0 mt-3 p-3" style="background: rgba(225, 29, 72, 0.1); border: 1px solid rgba(225, 29, 72, 0.2) !important;">
          <div class="d-flex align-items-center gap-2">
            <IconTicket :size="16" class="color-rose" />
            <span class="small fw-medium text-light">{{ shop.benefit_text }}</span>
          </div>
        </div>

        <!-- Links -->
        <div class="d-flex flex-wrap gap-2 mt-3">
          <a v-if="shop.website_url" :href="shop.website_url" target="_blank" class="btn btn-dark btn-sm">
            <IconExternalLink :size="14" class="me-1" />Web
          </a>
          <a v-if="shop.instagram_url" :href="shop.instagram_url" target="_blank" class="btn btn-dark btn-sm">Instagram</a>
          <a v-if="shop.tabelog_url" :href="shop.tabelog_url" target="_blank" class="btn btn-dark btn-sm">食べログ</a>
          <a v-if="shop.google_map_url" :href="shop.google_map_url" target="_blank" class="btn btn-dark btn-sm">Google Map</a>
        </div>

        <!-- Coupons -->
        <section v-if="coupons.length" class="mt-4 mb-5">
          <h3 class="small fw-semibold text-secondary mb-3">クーポン</h3>
          <div class="d-flex flex-column gap-3">
            <div v-for="c in coupons" :key="c.id" class="card bg-dark border-0 p-3">
              <div class="fw-medium small">{{ c.title }}</div>
              <div v-if="c.discount_text" class="tiny color-rose mt-1">{{ c.discount_text }}</div>
              <div v-if="c.description" class="tiny text-secondary mt-1">{{ c.description }}</div>
              <div v-if="c.conditions" class="tiny text-secondary">{{ c.conditions }}</div>

              <template v-if="auth.isAuthenticated">
                <button
                  @click="useCoupon(c)"
                  :disabled="couponStates[c.id]?.loading"
                  class="btn btn-primary-rose btn-sm mt-2"
                >
                  {{ couponStates[c.id]?.loading ? '処理中...' : '利用する' }}
                </button>
              </template>
              <p v-else class="tiny text-secondary mt-2 mb-0">ログインしてクーポンを利用</p>

              <!-- Feedback -->
              <div v-if="couponStates[c.id]?.msg" class="mt-2">
                <div v-if="couponStates[c.id].type === 'success'" class="d-flex align-items-center gap-1 small color-green">
                  <IconCheck :size="14" />{{ couponStates[c.id].msg }}
                </div>
                <div v-else-if="couponStates[c.id].type === 'cooldown'" class="d-flex align-items-center gap-1 small color-amber">
                  <IconClock :size="14" />{{ couponStates[c.id].msg }}
                </div>
                <div v-else class="small text-danger">{{ couponStates[c.id].msg }}</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
