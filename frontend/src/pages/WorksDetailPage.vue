<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import WorksBody from '@/components/WorksBody.vue'
import AsyncImage from '@/components/AsyncImage.vue'
import { request } from '@/apiClient'

const props = defineProps(['id'])
const work = ref(null)
const loading = ref(true)
const error = ref(null)
const route = useRoute()

async function fetchWork() {
  loading.value = true
  try {
    const workId = props.id || route.params.id
    console.log('[HOSHIDORI] Fetching work detail for id:', workId)
    const workData = await request(`/api/works/${workId}/`)
    console.log('[HOSHIDORI] Work detail fetched:', workData)
    work.value = workData
    if (!work.value) {
      error.value = '作品が見つかりません'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchWork)
</script>

<template>
  <main class="container py-4">
    <p v-if="loading">読み込み中...</p>
    <p v-else-if="error">エラー: {{ error }}</p>
    <p v-else-if="!work">作品が見つかりません。</p>

    <div v-else class="wrap">
      <div class="h-100">
        <!-- 画像コンテナ -->
        <div class="position-relative my-4" style="overflow: hidden;">
          <AsyncImage
            v-if="work.main_image || work.main_image_url"
            :src="work.main_image || work.main_image_url"
            :alt="work.title"
            aspectRatio="1 / 1.414"
          />
          <div 
            v-else 
            class="bg-secondary d-flex align-items-center justify-content-center text-white"
            style="aspect-ratio: 1/1.414;"
          >
            画像なし
          </div>

          <!-- 許諾申請中のオーバーレイ -->
          <div 
            v-if="(work.main_image || work.main_image_url) && work.troupe && !work.troupe.image_allowed"
            class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
            style="background-color: rgba(0, 0, 0, 0.7); z-index: 5;"
          >
            <div class="text-center text-white">
              <div style="font-size: 16px; font-weight: bold;">
                {{ work.troupe?.name || '劇団' }}様に<br>許諾申請中
              </div>
            </div>
          </div>
        </div>
        
        <WorksBody :work="work" />
      </div>
    </div>
  </main>
</template>
