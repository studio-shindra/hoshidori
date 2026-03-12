<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (password.value !== passwordConfirm.value) {
    error.value = 'パスワードが一致しません'
    return
  }
  loading.value = true
  try {
    await auth.register({
      username: username.value,
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    await auth.fetchMe()
    router.push('/')
  } catch (e) {
    const d = e.data
    if (d) {
      error.value = Object.values(d).flat().join(' ')
    } else {
      error.value = '登録に失敗しました'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="px-3 pt-5" style="max-width: 360px; margin: 0 auto;">
    <h2 class="fs-5 fw-bold text-center mb-4">新規登録</h2>
    <form @submit.prevent="submit" class="d-flex flex-column gap-3">
      <input v-model="username" placeholder="ユーザー名" required autocomplete="username" class="form-control bg-dark border-secondary text-light" />
      <input v-model="email" type="email" placeholder="メールアドレス" required class="form-control bg-dark border-secondary text-light" />
      <input v-model="password" type="password" placeholder="パスワード" required autocomplete="new-password" class="form-control bg-dark border-secondary text-light" />
      <input v-model="passwordConfirm" type="password" placeholder="パスワード（確認）" required autocomplete="new-password" class="form-control bg-dark border-secondary text-light" />
      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <button type="submit" :disabled="loading" class="btn btn-primary-rose fw-medium">
        {{ loading ? '...' : '登録' }}
      </button>
    </form>
    <p class="text-center mt-3 small text-secondary">
      アカウントをお持ちの方は <RouterLink to="/login">ログイン</RouterLink>
    </p>
  </div>
</template>
