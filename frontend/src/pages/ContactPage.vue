<script setup>
import { ref } from 'vue'
import { sendContact } from '@/apiClient'

const name = ref('')
const email = ref('')
const message = ref('')

const sending = ref(false)
const success = ref(false)
const error = ref('')

async function handleSubmit(e) {
  e.preventDefault()
  error.value = ''
  success.value = false

  if (!name.value || !email.value || !message.value) {
    error.value = 'すべての項目を入力してください。'
    return
  }

  sending.value = true
  try {
    await sendContact({
      name: name.value,
      email: email.value,
      message: message.value,
    })
    success.value = true
    // フォーム初期化
    name.value = ''
    email.value = ''
    message.value = ''
  } catch (e) {
    console.error(e)
    error.value = '送信に失敗しました。時間をおいて再度お試しください。'
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3 fw-bold text-center fs-3">お問い合わせ</h1>

    <div v-if="success" class="alert alert-success">
      送信しました。返信をお待ちください。
    </div>
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <form @submit="handleSubmit" class="mx-auto" style="max-width: 600px;">
      <div class="mb-3">
        <label class="form-label">お名前</label>
        <input
          type="text"
          class="form-control"
          v-model="name"
          placeholder="お名前"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">メールアドレス</label>
        <input
          type="email"
          class="form-control"
          v-model="email"
          placeholder="example@example.com"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">お問い合わせ内容</label>
        <textarea
          class="form-control"
          rows="5"
          v-model="message"
          placeholder="お問い合わせ内容を入力してください"
        />
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100"
        :disabled="sending"
      >
        {{ sending ? '送信中...' : '送信する' }}
      </button>
    </form>
  </main>
</template>