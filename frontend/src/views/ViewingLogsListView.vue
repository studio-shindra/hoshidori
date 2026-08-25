<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '@/lib/api'
import LogListItem from '@/components/LogListItem.vue'

const tab = ref('planned')
const logs = ref([])
const loading = ref(true)

async function fetchLogs() {
  loading.value = true
  try {
    const data = await api.get(`/api/viewing-logs/?status=${tab.value}`)
    logs.value = data.results || data
  } catch {
    logs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)
watch(tab, fetchLogs)
</script>

<template>
  <div class="pt-4">
    <h1 class="fw-bold mb-3 fs-3">観劇記録</h1>
    <div class="d-flex gap-2 mb-3">
      <button
        class="btn flex-fill fw-medium"
        :class="tab === 'planned' ? 'btn-status-amber' : 'btn-dark text-secondary'"
        @click="tab = 'planned'"
      >観る</button>
      <button
        class="btn flex-fill fw-medium"
        :class="tab === 'watched' ? 'btn-status-green' : 'btn-dark text-secondary'"
        @click="tab = 'watched'"
      >観た</button>
    </div>

    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <template v-else>
      <div v-if="logs.length" class="d-flex flex-column gap-2">
        <LogListItem
          v-for="log in logs"
          :key="log.id"
          :work-title="log.work_title"
          :work-slug="log.work_slug"
          :watched-on="log.watched_on"
          :watched-time="log.watched_time"
          :theater-name="log.theater_name"
          :theater-area="log.theater_area"
          :memo="log.memo"
          :rating="log.rating"
          :after-shop-name="log.after_shop_name"
        />
      </div>
      <p v-else class="text-secondary text-center mt-4">まだ記録がありません</p>
    </template>

    <RouterLink to="/logs/new" class="btn btn-primary-rose w-100 fw-medium mt-3">＋ 記録する</RouterLink>
  </div>
</template>
