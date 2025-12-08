<script setup>
import { ref, onMounted } from 'vue'
import { currentUser } from '@/authState'
import { pickImageFromLibrary, isNativePlatform } from '@/lib/photoPicker'

const saving = ref(false)
const error = ref(null)
const successMessage = ref(null)

const form = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  profile_image: null,
})

const selectedFile = ref(null)
const previewUrl = ref(null)
const fileInputRef = ref(null)
const isNative = isNativePlatform()

onMounted(() => {
  if (currentUser.value) {
    form.value.username = currentUser.value.username || ''
    form.value.first_name = currentUser.value.first_name || ''
    form.value.last_name = currentUser.value.last_name || ''
    form.value.email = currentUser.value.email || ''
    if (currentUser.value.profile_image) {
      previewUrl.value = currentUser.value.profile_image
    }
  }
})

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return

  setSelectedFile(file)
}

function setSelectedFile(file, previewOverride = null) {
  selectedFile.value = file

  if (!file) {
    previewUrl.value = null
    return
  }

  if (previewOverride) {
    previewUrl.value = previewOverride
    return
  }

  const reader = new FileReader()
  reader.onload = (event) => {
    previewUrl.value = event.target?.result
  }
  reader.readAsDataURL(file)
}

async function startImageSelection() {
  if (isNative) {
    try {
      const { file, previewUrl: dataUrl } = await pickImageFromLibrary({
        fileName: 'profile.jpg',
        quality: 80,
      })
      setSelectedFile(file, dataUrl)
    } catch (err) {
      console.error('Photo pick failed:', err)
      alert('写真の取得に失敗しました。フォトライブラリのアクセス権限を確認してください。')
    }
    return
  }

  if (fileInputRef.value) {
    fileInputRef.value.value = ''
    fileInputRef.value.click()
  }
}

async function handleSave(e) {
  e.preventDefault()
  saving.value = true
  error.value = null
  successMessage.value = null

  try {
    // FormData でファイルを含める
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('first_name', form.value.first_name)
    formData.append('last_name', form.value.last_name)
    formData.append('email', form.value.email)

    if (selectedFile.value) {
      formData.append('profile_image', selectedFile.value)
    }

    // PATCH でプロフィール更新
    const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
    const res = await fetch(`${baseUrl}/api/auth/user/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('hoshidori_token')}`,
      },
      body: formData,
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || 'プロフィール更新に失敗しました')
    }

    const updated = await res.json()

    // currentUser を更新
    currentUser.value = { ...currentUser.value, ...updated }
    form.value.profile_image = updated.profile_image
    selectedFile.value = null

    successMessage.value = 'プロフィールを更新しました'
  } catch (e) {
    error.value = e.message || 'エラーが発生しました'
  } finally {
    saving.value = false
  }
}

async function handleDeleteAccount() {
  const ok = window.confirm('本当にアカウントを削除しますか？\nこの操作は取り消せません。')
  if (!ok) return

  saving.value = true
  error.value = null

  try {
    const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
    const res = await fetch(`${baseUrl}/api/auth/user/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('hoshidori_token')}`,
      },
    })

    if (!res.ok) {
      throw new Error('アカウント削除に失敗しました')
    }

    // ログアウト
    localStorage.removeItem('hoshidori_token')
    localStorage.removeItem('hoshidori_refresh')
    currentUser.value = null
    location.href = '/login'
  } catch (e) {
    error.value = e.message || 'エラーが発生しました'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="container py-4" style="max-width: 480px; margin-bottom: 100px;">
    <h1 class="mb-4 fw-bold text-center">設定</h1>

    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ successMessage }}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>

    <form @submit="handleSave" class="mb-4">
      <!-- プロフィール画像 -->
      <div class="wrap mb-4">
        <label class="form-label fw-bold">プロフィール画像</label>
        <div class="d-flex align-items-center gap-3 mb-3">
          <div
            class="profile-preview d-flex align-items-center justify-content-center"
            style="width: 80px; height: 80px; background: #f0f0f0; border-radius: 50%; flex-shrink: 0;"
          >
            <img
              v-if="previewUrl"
              :src="previewUrl"
              alt="preview"
              style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;"
            />
            <div v-else style="font-size: 32px; font-weight: bold; color: #999;">
              {{ currentUser?.username?.charAt(0).toUpperCase() || '?' }}
            </div>
          </div>
          <div class="d-flex flex-column flex-grow-1 gap-2">
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              class="d-none"
              @change="handleFileSelect"
            />
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="startImageSelection"
            >
              フォトライブラリから選択
            </button>
            <div class="small text-muted">カメラ撮影は今回のバージョンでは無効化しています。</div>
          </div>
        </div>
      </div>

      <!-- ユーザー名 -->
      <div class="wrap mb-3">
        <label class="form-label fw-bold">ユーザー名</label>
        <input
          v-model="form.username"
          type="text"
          class="form-control"
          placeholder="ユーザー名"
        />
      </div>

      <!-- 名前 -->
      <div class="wrap mb-3">
        <label class="form-label fw-bold">名</label>
        <input
          v-model="form.first_name"
          type="text"
          class="form-control"
          placeholder="名"
        />
      </div>

      <!-- 姓 -->
      <div class="wrap mb-3">
        <label class="form-label fw-bold">姓</label>
        <input
          v-model="form.last_name"
          type="text"
          class="form-control"
          placeholder="姓"
        />
      </div>

      <!-- メールアドレス -->
      <div class="wrap mb-4">
        <label class="form-label fw-bold">メールアドレス</label>
        <input
          v-model="form.email"
          type="email"
          class="form-control"
          placeholder="メールアドレス"
        />
      </div>

      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary flex-grow-1" :disabled="saving">
          変更を保存
        </button>
        <button
          type="button"
          class="btn btn-danger"
          @click="handleDeleteAccount"
          :disabled="saving"
        >
          アカウント削除
        </button>
      </div>
    </form>
  </main>
</template>

<style scoped>
.wrap {
  padding: 0 1rem;
}
</style>