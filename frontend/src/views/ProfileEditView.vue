<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const displayName = ref('')
const bio = ref('')
const saving = ref(false)
const message = ref('')
const messageType = ref('')

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage/edit' } })
    return
  }
  displayName.value = auth.user.display_name || ''
  bio.value = auth.user.bio || ''
})

async function save() {
  saving.value = true
  message.value = ''
  try {
    const data = await api.patch('/api/auth/me/', {
      display_name: displayName.value,
      bio: bio.value,
    })
    auth.user.display_name = data.display_name
    auth.user.bio = data.bio
    message.value = '保存しました'
    messageType.value = 'success'
    setTimeout(() => router.push('/mypage'), 800)
  } catch {
    message.value = '保存に失敗しました'
    messageType.value = 'danger'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="px-3 pt-4 pb-3">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h2 class="fs-5 fw-bold mb-0">プロフィール編集</h2>
      <RouterLink to="/mypage" class="btn btn-sm btn-dark text-secondary">戻る</RouterLink>
    </div>

    <!-- Current profile preview -->
    <div class="card bg-dark border-0 p-3 mb-4">
      <div class="d-flex align-items-center gap-3">
        <div class="avatar-circle">
          {{ (auth.user?.display_name || auth.user?.username || '?').charAt(0) }}
        </div>
        <div>
          <div class="fw-semibold">{{ auth.user?.display_name || auth.user?.username }}</div>
          <div class="tiny text-secondary">@{{ auth.user?.username }}</div>
        </div>
      </div>
    </div>

    <!-- Edit form -->
    <div class="mb-3">
      <label class="form-label small text-secondary">表示名</label>
      <input
        v-model="displayName"
        type="text"
        class="form-control bg-dark border-secondary text-light"
        maxlength="100"
        placeholder="表示名を入力"
      />
      <div class="tiny text-secondary mt-1">{{ displayName.length }} / 100</div>
    </div>

    <div class="mb-4">
      <label class="form-label small text-secondary">自己紹介</label>
      <textarea
        v-model="bio"
        class="form-control bg-dark border-secondary text-light"
        rows="4"
        maxlength="500"
        placeholder="観劇の好みや自己紹介など"
      ></textarea>
      <div class="tiny text-secondary mt-1">{{ bio.length }} / 500</div>
    </div>

    <!-- Message -->
    <div v-if="message" class="alert py-2 small" :class="`alert-${messageType}`">
      {{ message }}
    </div>

    <!-- Buttons -->
    <div class="d-flex gap-2">
      <button class="btn btn-primary-rose flex-grow-1 fw-medium" :disabled="saving" @click="save">
        {{ saving ? '保存中...' : '保存する' }}
      </button>
      <RouterLink to="/mypage" class="btn btn-dark text-secondary flex-grow-1 text-center">キャンセル</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #27272a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 600;
  color: #a1a1aa;
  flex-shrink: 0;
}
.tiny {
  font-size: 0.7rem;
}
</style>
