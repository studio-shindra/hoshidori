<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

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
    router.push(route.query.next || '/')
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
      アカウントをお持ちの方は <RouterLink :to="{ path: '/login', query: route.query.next ? { next: route.query.next } : {} }">ログイン</RouterLink>
    </p>
    <p class="tiny text-secondary text-center mt-4 mb-2">登録すると利用規約とプライバシーポリシーに同意したものとみなされます。</p>
    <nav class="auth-legal-links" aria-label="規約とお問い合わせ">
      <RouterLink to="/terms">利用規約</RouterLink>
      <RouterLink to="/privacy">プライバシー</RouterLink>
      <RouterLink to="/contact">お問い合わせ</RouterLink>
    </nav>
  </div>
</template>

<style scoped>
.auth-legal-links { display: flex; justify-content: center; flex-wrap: wrap; gap: .6rem 1rem; }
.auth-legal-links a { color: #71717a; font-size: .64rem; text-decoration: none; }
</style>
