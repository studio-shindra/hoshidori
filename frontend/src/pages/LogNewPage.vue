<!-- src/pages/LogNewPage.vue -->
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { request, rateWork } from '@/apiClient'
import { onLogSaveSuccess } from '@/lib/admobHelpers'
import { currentUser } from '@/authState'
import { createLocalLog, isGuestUser } from '@/lib/localLogs'
import LogForm from '@/components/LogForm.vue'

const router = useRouter()
const saving = ref(false)
const isGuest = computed(() => isGuestUser() || !currentUser.value)

async function handleCreate(payload) {
  saving.value = true
  try {
    if (isGuest.value) {
      createLocalLog(payload)
      // rating だけサーバへ送信して平均を更新
      if (payload.work_id && payload.rating) {
        try {
          await rateWork(payload.work_id, payload.rating)
        } catch (err) {
          console.warn('rating送信に失敗しましたがローカル保存は完了:', err)
        }
      }

      alert('保存しました！')
      router.push('/logs')
    } else {
      await request('/api/logs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      // 保存成功：インタースティシャル広告を表示（3回に1回）
      await onLogSaveSuccess()

      alert('保存しました！')

      // 一度リロードして最新ログを確実に反映
      window.location.href = '/logs'
    }

  } catch (error) {
    console.error('ログの保存に失敗しました:', error)
    alert('ログの保存に失敗しました。もう一度お試しください。')
  } finally {
    saving.value = false
  }
}

</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3 fw-bold text-center fs-3">観劇ログを追加</h1>
    <LogForm 
      mode="create" 
      :loading="saving" 
      @submit="handleCreate" 
    />
  </main>
</template>
