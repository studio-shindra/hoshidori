<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { currentUser } from '@/authState'
import { syncLocalDataToServer } from '@/lib/syncData'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const message = ref('')

const redirectTo = route.query.redirect || '/logs'

async function handleLogin(e) {
  e.preventDefault()
  loading.value = true
  error.value = null
  message.value = ''

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
    const url = `${baseUrl}/api/auth/token/`
    
    console.log('[HOSHIDORI LOGIN] baseUrl:', baseUrl)
    console.log('[HOSHIDORI LOGIN] URL:', url)
    console.log('[HOSHIDORI LOGIN] username:', username.value)
    
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        // Djangoデフォルトは username フィールド
        username: username.value,
        password: password.value,
      }),
    })
    
    console.log('[HOSHIDORI LOGIN] Response status:', res.status)

    if (!res.ok) {
      const text = await res.text()
      console.error('[HOSHIDORI LOGIN] Error response:', text)
      
      // エラーメッセージを日本語化
      let errorMessage = 'ログインに失敗しました'
      if (res.status === 401) {
        errorMessage = 'ユーザー名またはパスワードが違います'
      } else if (res.status === 400) {
        errorMessage = '入力内容に誤りがあります'
      } else if (res.status >= 500) {
        errorMessage = 'サーバーエラーが発生しました。しばらくしてから再度お試しください'
      }
      throw new Error(errorMessage)
    }

    const data = await res.json()
    // { access, refresh }
    localStorage.setItem('hoshidori_token', data.access)
    localStorage.setItem('hoshidori_refresh', data.refresh)

    // ユーザープロフィール取得
    const userRes = await fetch(`${baseUrl}/api/auth/user/`, {
      headers: { Authorization: `Bearer ${data.access}` },
    })
    const userProfile = userRes.ok ? await userRes.json() : {}

    // currentUser にプロフィール情報を保存
    currentUser.value = { token: data.access, ...userProfile }
    
    // ローカルデータをサーバーに同期
    message.value = 'ログインしました。ローカルデータを同期中...'
    const synced = await syncLocalDataToServer()
    if (synced) {
      message.value = 'ログインしました。データを同期しました！'
    } else {
      message.value = 'ログインしました'
    }
    
    // 同期完了後にリダイレクト
    setTimeout(() => {
      router.push(redirectTo)
    }, 1500)
  } catch (e) {
    console.error(e)
    error.value = e.message || 'ログインに失敗しました'
  } finally {
    loading.value = false
  }
}

// サインアップは別ページに移動
</script>

<template>
  <main class="container" style="max-width: 480px; padding-top: 6rem;">
    <h1 class="mb-4 d-flex flex-column align-items-center">
      <img src="/icon.svg" width="40" alt="">
    </h1>

    <!-- ログインオプション説明 -->
    <div class="alert alert-light text-center mb-4" style="font-size: 14px; border: 1px solid #ddd;">
      <p class="mb-0">
        <strong>ログインは不要でも使えます</strong><br>
        <small class="text-muted">データのバックアップ・複数端末での同期に便利です</small>
      </p>
    </div>

    <form @submit="handleLogin" class="mb-3">
      <div class="mb-3">
        <input
          v-model="username"
          type="text"
          class="form-control"
          autocomplete="username"
          placeholder="ユーザー名"
          required
        />
      </div>

      <div class="mb-3">
        <input
          v-model="password"
          type="password"
          class="form-control"
          autocomplete="current-password"
          placeholder="パスワード"
          required
        />
      </div>

      <button type="submit" class="btn btn-primary w-100" :disabled="loading">
        {{ loading ? '処理中...' : 'ログイン' }}
      </button>
    </form>

    <router-link
      class="btn btn-link w-100 mb-2"
      :class="{ disabled: loading }"
      to="/signup"
    >
      初めての方
    </router-link>

    <p v-if="error" class="text-danger mt-2">{{ error }}</p>
    <p v-if="message" class="text-success mt-2">{{ message }}</p>
  </main>
</template>