<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { IconStar, IconHeart } from '@tabler/icons-vue'

const auth = useAuthStore()
const router = useRouter()

const planned = ref([])
const watched = ref([])
const myReviews = ref([])
const loading = ref(true)

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage' } })
    return
  }
  try {
    const [pData, wData, rData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
      api.get('/api/reviews/'),
    ])
    planned.value = pData.results || pData
    watched.value = wData.results || wData
    const allReviews = rData.results || rData
    const me = auth.user
    myReviews.value = allReviews.filter(
      (r) => r.user === me.id || r.username === me.username,
    )
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

async function logout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="px-3 pt-4">
    <h2 class="fs-5 fw-bold mb-3">マイページ</h2>
    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <template v-else>
      <div class="mb-3">
        <div class="fs-6 fw-semibold">{{ auth.user.display_name || auth.user.username }}</div>
        <div v-if="auth.user.role" class="tiny text-secondary">{{ auth.user.role }}</div>
      </div>

      <!-- Stats -->
      <div class="row g-2 mb-4">
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold color-amber">{{ planned.length }}</div>
            <div class="small text-secondary">これから観る</div>
          </div>
        </div>
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold color-green">{{ watched.length }}</div>
            <div class="small text-secondary">観た</div>
          </div>
        </div>
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold text-light">{{ myReviews.length }}</div>
            <div class="small text-secondary">感想</div>
          </div>
        </div>
      </div>

      <!-- My reviews -->
      <section v-if="myReviews.length" class="mb-4">
        <h3 class="small fw-semibold text-secondary mb-3">自分の感想</h3>
        <div class="d-flex flex-column gap-2">
          <div v-for="r in myReviews" :key="r.id" class="card bg-dark border-0 p-3">
            <div class="d-flex justify-content-between mb-1">
              <span v-if="r.rating_overall" class="small color-amber">
                <IconStar :size="14" /> {{ r.rating_overall }}
              </span>
              <span class="tiny text-secondary">
                <IconHeart :size="12" /> {{ r.like_count || 0 }}
              </span>
            </div>
            <p class="small text-light mb-0 lh-base">{{ r.body }}</p>
          </div>
        </div>
      </section>

      <button class="btn btn-dark w-100 text-secondary mt-2" @click="logout">ログアウト</button>
    </template>
  </div>
</template>
