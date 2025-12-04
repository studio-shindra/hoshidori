<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { IconX, IconEdit, IconShare, IconBrandAmazon, IconBinoculars } from '@tabler/icons-vue'
import WorksBody from '@/components/WorksBody.vue'
import { request } from '@/apiClient'
import SimpleSpinner from '@/components/LoadingSimpleSpinner.vue'

const props = defineProps(['id'])
const log = ref(null)
const loading = ref(true)
const error = ref(null)
const router = useRouter()
const route = useRoute()

async function fetchLog() {
  loading.value = true
  try {
    const logId = props.id || route.params.id
    const logs = await request('/api/logs/')
    log.value = logs.find(l => l.id === Number(logId))
    if (!log.value) {
      error.value = 'ログが見つかりません'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchLog)

function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

async function deleteLog() {
  const ok = window.confirm('この観劇ログを削除しますか？')
  if (!ok) return

  await request(`/api/logs/${log.value.id}/`, {
    method: 'DELETE',
  })

  router.push('/logs')
}
</script>

<template>
  <main class="container py-4">
    <p v-if="loading">
      <div class="df-center">
        <SimpleSpinner />
      </div>      
    </p>
    <p v-else-if="error">エラー: {{ error }}</p>
    <p v-else-if="!log">ログが見つかりません。</p>

    <div v-else class="wrap">
        <div class="h-100 position-relative">
          <div class="position-absolute end-0 top-0 m-2">
            <button
              type="button"
              class="btn btn-sm"
              @click="deleteLog"
            >
              <IconX />
            </button>
          </div>
          <img 
            v-if="log.work?.main_image || log.work?.main_image_url" 
            :src="log.work?.main_image || log.work?.main_image_url" 
            class="card-img-top w-100 h-100"
            :alt="log.work.title"
          >
          <div 
            v-else 
            class="card-img-top bg-secondary d-flex align-items-center justify-content-center text-white"
            style="aspect-ratio: 1/1.414; cursor: pointer;">
            画像なし
          </div>
          
          <WorksBody :work="log.work" />
          
          <div v-if="log.memo" class="card-text mt-3">
            <div class="d-flex align-items-center mb-1"><IconBinoculars /><small>{{ formatDate(log.watched_at) }}</small></div>
            <p class="mt-2 pt-2 border-top py-4">
              {{ log.memo }}
            </p>
          </div>

          <div class="d-flex justify-content-center mt-3">
              <div
                class="d-inline-flex gap-2 text-secondary bg-light px-3 py-2"
                style="border-radius: 100px;">
                <router-link
                  :to="`/logs/${log.id}/edit`"
                  class="btn btn-sm"
                >
                  <IconEdit />
                </router-link>
                <button
                  class="btn btn-sm">
                  <IconBrandAmazon />
                </button>
                <button
                  class="btn btn-sm">
                  <IconShare />
                </button>
              </div>
            </div>
        </div>
    </div>
  </main>
</template>