<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft } from '@tabler/icons-vue'

const router = useRouter()
const title = ref('')
const description = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!title.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    const work = await api.post('/api/works/', {
      title: title.value.trim(),
      description: description.value.trim(),
    })
    router.push(`/works/${work.slug}`)
  } catch (e) {
    error.value = e.data ? Object.values(e.data).flat().join(' ') : '作成に失敗しました'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center gap-2 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">作品を登録</h1>
    </header>

    <form @submit.prevent="submit" class="px-3 d-flex flex-column gap-3">
      <div>
        <label class="form-label tiny text-secondary">タイトル *</label>
        <input
          v-model="title"
          type="text"
          required
          placeholder="作品タイトル"
          class="form-control bg-dark border-secondary text-light"
        />
      </div>
      <div>
        <label class="form-label tiny text-secondary">説明（任意）</label>
        <textarea
          v-model="description"
          rows="3"
          placeholder="作品の説明"
          class="form-control bg-dark border-secondary text-light"
        ></textarea>
      </div>
      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <button type="submit" :disabled="loading || !title.trim()" class="btn btn-primary-rose w-100 fw-medium py-2">
        {{ loading ? '作成中...' : '作品を登録' }}
      </button>
      <p class="tiny text-secondary">slug は自動生成されます。登録後に作品ページへ移動します。</p>
    </form>
  </div>
</template>
