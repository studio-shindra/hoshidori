<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import WorksBody from '@/components/WorksBody.vue'
import { IconSearch, IconStarFilled } from '@tabler/icons-vue'
import { fetchWorks } from '@/apiClient'

const route = useRoute()
const q = ref(route.query.q || '')
const works = ref([])
const loading = ref(false)
const error = ref(null)

async function search() {
  loading.value = true
  error.value = null
  works.value = []

  try {
    const params = {}
    if (q.value.trim()) params.search = q.value.trim()
    const data = await fetchWorks(params)
    works.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 初期表示：全作品を取得
onMounted(() => {
  search()
})
</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3 fs-3 fw-bold text-center">作品一覧</h1>
    <form class="position-relative mb-5" @submit.prevent="search">
      <div class="input">
        <input
          v-model="q"
          type="search"
          class="form-control"
          placeholder="タイトル・劇場名・俳優名などで検索"
        />
      </div>
      <div class="position-absolute end-0 top-0 bottom-0 d-flex align-items-center me-2">
        <button type="submit" class="btn btn-sm" style="z-index: 999;">
          <IconSearch :size="20"/> 
        </button>
      </div>
    </form>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="error" class="text-danger">エラー: {{ error }}</p>
    <p v-else-if="works.length === 0">作品がありません。</p>

    <div v-if="works.length > 0" class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-1">
      <div v-for="work in works" :key="work.id" class="col position-relative">
        <router-link :to="`/works/${work.id}/detail`" class="text-decoration-none">
          <div class="card h-100 border-0 shadow-sm">
            <!-- 評価バッジ（画像の上に重ねる） -->
            <div class="position-absolute bottom-0 end-0 p-2 bg-white" style="z-index: 10; aspect-ratio: 1/1; border-radius: 10px 0 0 0;">
              <span
                class="d-inline-flex align-items-center flex-column justify-content-center gap-1"
                style="color: orange;">
                <IconStarFilled :size="14" />
                {{ work.avg_rating || '-' }}
              </span>
            </div>
            
            <img
              v-if="work.main_image || work.main_image_url"
              :src="work.main_image || work.main_image_url"
              class="card-img-top"
              :alt="work.title"
              style="height: 250px; object-fit: cover;"
            />
            <div 
              v-else 
              class="card-img-top bg-secondary d-flex align-items-center justify-content-center text-white"
              style="height: 250px;"
            >
              画像なし
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </main>
</template>
