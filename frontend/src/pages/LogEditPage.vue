<!-- src/pages/LogEditPage.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '@/apiClient'
import LogForm from '@/components/LogForm.vue'
import SimpleSpinner from '@/components/LoadingSimpleSpinner.vue'

const router = useRouter()
const route = useRoute()

const log = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref(null)

async function fetchLog() {
  loading.value = true
  try {
    const logId = route.params.id
    const data = await request(`/api/logs/${logId}/`)
    log.value = data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleUpdate(payload) {
  saving.value = true
  try {
    await request(`/api/logs/${route.params.id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    router.push(`/logs/${route.params.id}`)
  } catch (error) {
    console.error('ログの更新に失敗しました:', error)
    alert('ログの更新に失敗しました。もう一度お試しください。')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  const ok = window.confirm('この観劇ログを削除しますか？')
  if (!ok) return

  saving.value = true
  try {
    await request(`/api/logs/${route.params.id}/`, {
      method: 'DELETE',
    })

    router.push('/logs')
  } catch (error) {
    console.error('ログの削除に失敗しました:', error)
    alert('ログの削除に失敗しました。もう一度お試しください。')
  } finally {
    saving.value = false
  }
}

onMounted(fetchLog)
</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3 fw-bold text-center fs-3">観劇ログを編集</h1>

    <SimpleSpinner :show="loading" />
    
    <p v-if="error">エラー: {{ error }}</p>

    <LogForm 
      v-if="!loading && !error && log"
      mode="edit" 
      :initial-value="log"
      :loading="saving" 
      @submit="handleUpdate"
      @delete="handleDelete"
    />
  </main>
</template>
