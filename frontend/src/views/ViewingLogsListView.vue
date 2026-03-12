<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '@/lib/api'

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
  <div class="px-3 pt-4">
    <h2 class="fs-5 fw-bold mb-3">観劇メモ</h2>
    <div class="d-flex gap-2 mb-3">
      <button
        class="btn flex-fill fw-medium"
        :class="tab === 'planned' ? 'btn-status-amber' : 'btn-dark text-secondary'"
        @click="tab = 'planned'"
      >これから観る</button>
      <button
        class="btn flex-fill fw-medium"
        :class="tab === 'watched' ? 'btn-status-green' : 'btn-dark text-secondary'"
        @click="tab = 'watched'"
      >観た</button>
    </div>

    <p v-if="loading" class="text-secondary">読み込み中...</p>
    <template v-else>
      <div v-if="logs.length" class="d-flex flex-column gap-2">
        <div v-for="log in logs" :key="log.id" class="card bg-dark border-0 p-3">
          <div class="fw-medium small">{{ log.performance_display || `公演 #${log.performance}` }}</div>
          <div v-if="log.watched_on" class="tiny text-secondary mt-1">{{ log.watched_on }}</div>
          <div v-if="log.memo" class="tiny text-secondary mt-1">{{ log.memo }}</div>
        </div>
      </div>
      <p v-else class="text-secondary text-center mt-4">まだ記録がありません</p>
    </template>

    <RouterLink to="/logs/new" class="btn btn-primary-rose w-100 fw-medium mt-3">＋ 記録する</RouterLink>
  </div>
</template>
