<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    await auth.fetchMe()
    router.push(route.query.next || '/')
  } catch (e) {
    error.value = e.data?.detail || e.data?.non_field_errors?.[0] || 'ログインに失敗しました'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="px-3 pt-5" style="max-width: 360px; margin: 0 auto;">
    <h2 class="fs-5 fw-bold text-center mb-4">ログイン</h2>
    <form @submit.prevent="submit" class="d-flex flex-column gap-3">
      <input
        v-model="username"
        placeholder="ユーザー名"
        required
        autocomplete="username"
        class="form-control bg-dark border-secondary text-light"
      />
      <input
        v-model="password"
        type="password"
        placeholder="パスワード"
        required
        autocomplete="current-password"
        class="form-control bg-dark border-secondary text-light"
      />
      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <button type="submit" :disabled="loading" class="btn btn-primary-rose fw-medium">
        {{ loading ? '...' : 'ログイン' }}
      </button>
    </form>
    <p class="text-center mt-3 small text-secondary">
      アカウントがない方は <RouterLink to="/register">新規登録</RouterLink>
    </p>
  </div>
</template>
