<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const message = ref('')

async function handleRegister(e) {
	e.preventDefault()
	loading.value = true
	error.value = null
	message.value = ''

	try {
		const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
		const res = await fetch(`${baseUrl}/api/auth/register/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username: username.value, email: email.value, password: password.value })
		})

		const text = await res.text()
		if (!res.ok) {
			throw new Error(text || `Sign up failed: ${res.status}`)
		}

		message.value = '登録に成功しました。ログインしてください。'
		setTimeout(() => router.push({ name: 'login' }), 800)
	} catch (e) {
		console.error(e)
		error.value = e.message || 'サインアップに失敗しました'
	} finally {
		loading.value = false
	}
}
</script>

<template>
	<main class="container py-5" style="max-width: 480px">
		<h1 class="mb-4 fw-bold text-center">新規登録</h1>

		<!-- サインアップオプション説明 -->
		<div class="alert alert-light text-center mb-4" style="font-size: 14px; border: 1px solid #ddd;">
			<p class="mb-0">
				<strong>アカウント登録は任意です</strong><br>
				<small class="text-muted">データのバックアップ・複数端末での同期に便利です</small>
			</p>
		</div>

		<form @submit="handleRegister" class="mb-3">
			<div class="mb-3">
				<label class="form-label">ユーザー名</label>
				<input v-model="username" type="text" class="form-control" autocomplete="username" required />
			</div>
			<div class="mb-3">
				<label class="form-label">メールアドレス</label>
				<input v-model="email" type="email" class="form-control" autocomplete="email" />
			</div>
			<div class="mb-3">
				<label class="form-label">パスワード</label>
				<input v-model="password" type="password" class="form-control" autocomplete="new-password" required />
			</div>
			<button type="submit" class="btn btn-primary w-100" :disabled="loading">
				{{ loading ? '処理中...' : '登録する' }}
			</button>
		</form>

		<p v-if="error" class="text-danger mt-2">{{ error }}</p>
		<p v-if="message" class="text-success mt-2">{{ message }}</p>
	</main>
  
</template>