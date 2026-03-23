<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { IconCamera, IconX } from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET

const auth = useAuthStore()
const router = useRouter()

const displayName = ref('')
const bio = ref('')
const avatarUrl = ref('')
const avatarUploading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('')
const showDeleteModal = ref(false)
const deleting = ref(false)

const fileInput = ref(null)

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage/edit' } })
    return
  }
  displayName.value = auth.user.display_name || ''
  bio.value = auth.user.bio || ''
  avatarUrl.value = auth.user.avatar_url || ''
})

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  avatarUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('upload_preset', UPLOAD_PRESET)
    const res = await fetch(
      `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
      { method: 'POST', body: fd },
    )
    if (!res.ok) throw new Error()
    const data = await res.json()
    avatarUrl.value = data.secure_url
    // 即座にDBに保存 & auth storeに反映
    const saved = await api.patch('/api/auth/me/', { avatar_url: data.secure_url })
    auth.user.avatar_url = saved.avatar_url
  } catch {
    message.value = 'アップロードに失敗しました'
    messageType.value = 'danger'
  } finally {
    avatarUploading.value = false
  }
}

async function removeAvatar() {
  avatarUploading.value = true
  try {
    const saved = await api.patch('/api/auth/me/', { avatar_url: '' })
    avatarUrl.value = ''
    auth.user.avatar_url = saved.avatar_url
  } catch {
    message.value = '画像の削除に失敗しました'
    messageType.value = 'danger'
  } finally {
    avatarUploading.value = false
  }
}

async function save() {
  saving.value = true
  message.value = ''
  try {
    const data = await api.patch('/api/auth/me/', {
      display_name: displayName.value,
      bio: bio.value,
      avatar_url: avatarUrl.value,
    })
    auth.user.display_name = data.display_name
    auth.user.bio = data.bio
    auth.user.avatar_url = data.avatar_url
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

async function deleteAccount() {
  deleting.value = true
  try {
    await auth.deleteAccount()
    router.push({ name: 'login', query: { deleted: '1' } })
  } catch {
    message.value = 'アカウント削除に失敗しました'
    messageType.value = 'danger'
    showDeleteModal.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="px-3 pt-4 pb-3">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h2 class="fs-5 fw-bold mb-0">プロフィール編集</h2>
      <RouterLink to="/mypage" class="btn btn-sm btn-dark text-secondary">戻る</RouterLink>
    </div>

    <!-- Avatar -->
    <div class="card bg-dark border-0 p-3 mb-4">
      <div class="d-flex align-items-center gap-3">
        <div class="position-relative" style="cursor: pointer" @click="fileInput?.click()">
          <UserAvatar :src="avatarUrl" :name="displayName || auth.user?.display_name || auth.user?.username" :size="56" />
          <div class="avatar-edit-badge">
            <IconCamera :size="12" />
          </div>
          <button
            v-if="avatarUrl && !avatarUploading"
            class="avatar-delete-badge"
            @click="removeAvatar"
          >
            <IconX :size="12" />
          </button>
          <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="uploadAvatar" />
        </div>
        <div>
          <div class="fw-semibold">{{ auth.user?.display_name || auth.user?.username }}</div>
          <div class="tiny text-secondary">@{{ auth.user?.username }}</div>
          <div v-if="avatarUploading" class="tiny text-secondary">アップロード中...</div>
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

    <!-- Account Delete -->
    <hr class="border-secondary my-4" />
    <button class="btn btn-outline-danger btn-sm w-100" @click="showDeleteModal = true">
      アカウントを削除
    </button>

    <!-- Delete Confirm Modal -->
    <div v-if="showDeleteModal" class="modal-backdrop fade show" @click="showDeleteModal = false"></div>
    <div v-if="showDeleteModal" class="modal fade show d-block" tabindex="-1" @click.self="showDeleteModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-dark text-light border-secondary">
          <div class="modal-header border-secondary">
            <h5 class="modal-title fs-6">アカウント削除</h5>
            <button type="button" class="btn-close btn-close-white" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body small">
            アカウントを削除すると、保存された観劇ログやプロフィール情報は削除され、元に戻せません。<br />
            本当に削除しますか？
          </div>
          <div class="modal-footer border-secondary">
            <button class="btn btn-sm btn-dark text-secondary" @click="showDeleteModal = false">キャンセル</button>
            <button class="btn btn-sm btn-danger" :disabled="deleting" @click="deleteAccount">
              {{ deleting ? '削除中...' : '削除する' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.avatar-edit-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #e11d48;
  color: #fff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-delete-badge{
  position: absolute;
  top: 0;
  right: 0;
  background: white;
  color: black;
  border-radius: 50%;
  aspect-ratio: 1/1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  padding: 2px;
}
</style>
