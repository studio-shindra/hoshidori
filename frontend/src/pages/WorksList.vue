<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import WorksBody from '@/components/WorksBody.vue'
import AsyncImage from '@/components/AsyncImage.vue'
import { IconSearch, IconStarFilled } from '@tabler/icons-vue'
import { fetchWorks } from '@/apiClient'

const route = useRoute()
const router = useRouter()
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
    console.log('[HOSHIDORI] fetchWorks response:', data)
    works.value = Array.isArray(data) ? data : (data?.results || [])
    console.log('[HOSHIDORI] works.value after assignment:', works.value)
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
    <h1 class="mb-3 fs-3 fw-bold text-center">登録作品一覧</h1>
    <form class="position-relative mb-5" @submit.prevent="search">
      <div class="input">
        <input
          v-model="q"
          type="search"
          class="form-control"
          placeholder="タイトル・劇場名・俳優名などで検索"
          style="padding-left: 36px;"
        />
      </div>
      <div class="position-absolute start-0 top-0 bottom-0 d-flex align-items-center me-2">
        <button type="submit" class="btn btn-sm" style="z-index: 999;">
          <IconSearch :size="20"/> 
        </button>
      </div>
    </form>

    <p v-if="error" class="text-danger">エラー: {{ error }}</p>
    <div
      v-else-if="works.length === 0"
      class="df-center flex-column">
        <div class="text-center mb-2">
          まだ作品が登録されていません。<br>
          登録してみませんか？
        </div>
        <button
          type="button"
          class="btn btn-sm btn-link"
          @click="router.push('/works/new')"
        >
          作品登録ページ
        </button>
    </div>

    <div v-if="works.length > 0" class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-1">
      <div v-for="work in works" :key="work.id" class="col position-relative">
        <router-link :to="`/works/${work.id}/detail`" class="text-decoration-none">
          <div class="card h-100 border-0 shadow-sm position-relative">
            <!-- 評価バッジ（画像の上に重ねる） -->
            <div class="position-absolute bottom-0 end-0 p-2 bg-white" style="z-index: 10; aspect-ratio: 1/1; border-radius: 10px 0 0 0;">
              <span
                class="d-inline-flex align-items-center flex-column justify-content-center gap-1"
                style="color: orange;">
                <IconStarFilled :size="14" />
                {{ work.avg_rating || '-' }}
              </span>
            </div>
            
            <!-- 画像コンテナ -->
            <div class="position-relative" style="height: 250px; overflow: hidden;">
              <AsyncImage
                v-if="work.main_image || work.main_image_url"
                :src="work.main_image || work.main_image_url"
                :alt="work.title"
                aspectRatio="auto"
                :rounded="false"
                style="height: 100%;"
              />
              <div 
                v-else 
                class="card-img-top bg-secondary d-flex align-items-center justify-content-center text-white"
                style="height: 100%;"
              >
                画像なし
              </div>

              <!-- 許諾申請中のオーバーレイ -->
              <div 
                v-if="work.troupe && !work.troupe.image_allowed"
                class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                style="background-color: rgba(0, 0, 0, 0.7); z-index: 5;"
              >
                <div class="text-center text-white">
                  <div style="font-size: 14px; font-weight: bold;">
                    {{ work.troupe?.name || '劇団' }}様に<br>許諾申請中
                  </div>
                </div>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </main>
</template>
