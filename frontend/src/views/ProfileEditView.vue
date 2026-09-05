<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { IconArrowLeft, IconCamera, IconX } from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
const MAX_AVATAR_SIZE = 10 * 1024 * 1024
const AVATAR_OUTPUT_SIZE = 512

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
const cropViewport = ref(null)
const cropSource = ref('')
const cropViewportSize = ref(280)
const cropNaturalWidth = ref(0)
const cropNaturalHeight = ref(0)
const cropZoom = ref(1)
const cropOffsetX = ref(0)
const cropOffsetY = ref(0)
let cropImage = null
let dragStart = null

const cropImageStyle = computed(() => {
  if (!cropNaturalWidth.value || !cropNaturalHeight.value) return {}
  const scale = getCropScale()
  return {
    width: `${cropNaturalWidth.value * scale}px`,
    height: `${cropNaturalHeight.value * scale}px`,
    left: `calc(50% + ${cropOffsetX.value}px)`,
    top: `calc(50% + ${cropOffsetY.value}px)`,
  }
})

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage/edit' } })
    return
  }
  displayName.value = auth.user.display_name || ''
  bio.value = auth.user.bio || ''
  avatarUrl.value = auth.user.avatar_url || ''
})

function getCropScale() {
  const coverScale = Math.max(
    cropViewportSize.value / cropNaturalWidth.value,
    cropViewportSize.value / cropNaturalHeight.value,
  )
  return coverScale * cropZoom.value
}

function clampCropPosition() {
  if (!cropNaturalWidth.value || !cropNaturalHeight.value) return
  const scale = getCropScale()
  const maxX = Math.max(0, (cropNaturalWidth.value * scale - cropViewportSize.value) / 2)
  const maxY = Math.max(0, (cropNaturalHeight.value * scale - cropViewportSize.value) / 2)
  cropOffsetX.value = Math.max(-maxX, Math.min(maxX, cropOffsetX.value))
  cropOffsetY.value = Math.max(-maxY, Math.min(maxY, cropOffsetY.value))
}

async function selectAvatar(e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return
  if (!file.type.startsWith('image/') || file.size > MAX_AVATAR_SIZE) {
    message.value = '10MB以下の画像を選んでください'
    messageType.value = 'danger'
    return
  }
  closeCrop()
  const source = URL.createObjectURL(file)
  const image = new Image()
  image.onload = async () => {
    cropImage = image
    cropSource.value = source
    cropNaturalWidth.value = image.naturalWidth
    cropNaturalHeight.value = image.naturalHeight
    cropZoom.value = 1
    cropOffsetX.value = 0
    cropOffsetY.value = 0
    await nextTick()
    cropViewportSize.value = cropViewport.value?.clientWidth || 280
    clampCropPosition()
  }
  image.onerror = () => {
    URL.revokeObjectURL(source)
    message.value = '画像を読み込めませんでした'
    messageType.value = 'danger'
  }
  image.src = source
}

function closeCrop() {
  if (cropSource.value) URL.revokeObjectURL(cropSource.value)
  cropSource.value = ''
  cropImage = null
  dragStart = null
}

function startCropDrag(event) {
  event.currentTarget.setPointerCapture?.(event.pointerId)
  dragStart = {
    x: event.clientX,
    y: event.clientY,
    offsetX: cropOffsetX.value,
    offsetY: cropOffsetY.value,
  }
}

function moveCropDrag(event) {
  if (!dragStart) return
  cropOffsetX.value = dragStart.offsetX + event.clientX - dragStart.x
  cropOffsetY.value = dragStart.offsetY + event.clientY - dragStart.y
  clampCropPosition()
}

function endCropDrag() {
  dragStart = null
}

async function uploadAvatarFile(file) {
  avatarUploading.value = true
  message.value = ''
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
    return true
  } catch {
    message.value = 'アップロードに失敗しました'
    messageType.value = 'danger'
    return false
  } finally {
    avatarUploading.value = false
  }
}

async function confirmCrop() {
  if (!cropImage) return
  const scale = getCropScale()
  const renderedWidth = cropNaturalWidth.value * scale
  const renderedHeight = cropNaturalHeight.value * scale
  const left = (cropViewportSize.value - renderedWidth) / 2 + cropOffsetX.value
  const top = (cropViewportSize.value - renderedHeight) / 2 + cropOffsetY.value
  const sourceX = Math.max(0, -left / scale)
  const sourceY = Math.max(0, -top / scale)
  const sourceSize = cropViewportSize.value / scale
  const canvas = document.createElement('canvas')
  canvas.width = AVATAR_OUTPUT_SIZE
  canvas.height = AVATAR_OUTPUT_SIZE
  canvas.getContext('2d').drawImage(
    cropImage,
    sourceX,
    sourceY,
    sourceSize,
    sourceSize,
    0,
    0,
    AVATAR_OUTPUT_SIZE,
    AVATAR_OUTPUT_SIZE,
  )
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', .9))
  if (!blob) {
    message.value = '画像の編集に失敗しました'
    messageType.value = 'danger'
    return
  }
  const uploaded = await uploadAvatarFile(new File([blob], 'avatar.jpg', { type: 'image/jpeg' }))
  if (uploaded) closeCrop()
}

onBeforeUnmount(closeCrop)

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
    <header class="d-flex align-items-center justify-content-between mb-4">
      <RouterLink to="/mypage" class="btn btn-link text-secondary p-0 small text-decoration-none page-back">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </RouterLink>
      <h1 class="fs-6 fw-bold mb-0">プロフィール編集</h1>
      <div class="page-back-spacer"></div>
    </header>

    <!-- Avatar -->
    <div class="card bg-dark border-0 p-3 mb-4">
      <div class="d-flex align-items-center gap-3">
        <div class="position-relative avatar-picker-wrap">
          <button type="button" class="avatar-picker" aria-label="プロフィール写真を選ぶ" @click="fileInput?.click()">
            <UserAvatar :src="avatarUrl" :name="displayName || auth.user?.display_name || auth.user?.username" :size="56" />
            <span class="avatar-edit-badge" aria-hidden="true">
              <IconCamera :size="12" />
            </span>
          </button>
          <button
            v-if="avatarUrl && !avatarUploading"
            class="avatar-delete-badge"
            type="button"
            aria-label="プロフィール写真を削除"
            @click.stop="removeAvatar"
          >
            <IconX :size="12" />
          </button>
        </div>
        <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="selectAvatar" />
        <div>
          <div class="fw-semibold">{{ auth.user?.display_name || auth.user?.username }}</div>
          <div class="tiny text-secondary">@{{ auth.user?.username }}</div>
          <div v-if="avatarUploading" class="tiny text-secondary">アップロード中...</div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="cropSource" class="avatar-crop-backdrop" @click.self="closeCrop">
        <section class="avatar-crop-dialog" role="dialog" aria-modal="true" aria-labelledby="avatarCropTitle">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <div>
              <h2 id="avatarCropTitle" class="fs-6 fw-bold mb-1">プロフィール写真を調整</h2>
              <p class="tiny text-secondary mb-0">ドラッグして位置を、バーで大きさを調整できます。</p>
            </div>
            <button type="button" class="btn-close btn-close-white" aria-label="画像編集を閉じる" @click="closeCrop"></button>
          </div>
          <div
            ref="cropViewport"
            class="avatar-crop-viewport"
            @pointerdown="startCropDrag"
            @pointermove="moveCropDrag"
            @pointerup="endCropDrag"
            @pointercancel="endCropDrag"
          >
            <img :src="cropSource" :style="cropImageStyle" alt="プロフィール写真の切り抜きプレビュー" draggable="false" />
          </div>
          <div class="avatar-zoom-row">
            <span aria-hidden="true">−</span>
            <input v-model.number="cropZoom" type="range" min="1" max="3" step="0.01" aria-label="画像の拡大率" @input="clampCropPosition" />
            <span aria-hidden="true">＋</span>
          </div>
          <div class="d-flex gap-2 mt-3">
            <button type="button" class="btn btn-primary-rose flex-fill fw-medium" :disabled="avatarUploading" @click="confirmCrop">
              {{ avatarUploading ? '保存中...' : 'この写真にする' }}
            </button>
            <button type="button" class="btn btn-dark flex-fill text-secondary" :disabled="avatarUploading" @click="closeCrop">キャンセル</button>
          </div>
        </section>
      </div>
    </Teleport>

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
            <button type="button" class="btn-close btn-close-white" aria-label="退会確認を閉じる" @click="showDeleteModal = false"></button>
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
.avatar-picker-wrap {
  width: 56px;
  height: 56px;
}
.avatar-picker {
  position: relative;
  display: block;
  width: 56px;
  height: 56px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  cursor: pointer;
}
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
.avatar-crop-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100001;
  display: grid;
  padding: max(1rem, env(safe-area-inset-top)) 1rem max(1rem, env(safe-area-inset-bottom));
  place-items: center;
  background: rgba(0,0,0,.82);
}
.avatar-crop-dialog {
  width: min(100%, 380px);
  padding: 1.25rem;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: #18181b;
  box-shadow: 0 24px 70px rgba(0,0,0,.5);
}
.avatar-crop-viewport {
  position: relative;
  width: min(72vw, 280px);
  aspect-ratio: 1;
  margin: 0 auto;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,.88);
  border-radius: 50%;
  background: #09090b;
  box-shadow: 0 0 0 999px rgba(0,0,0,.08);
  cursor: grab;
  touch-action: none;
  user-select: none;
}
.avatar-crop-viewport:active { cursor: grabbing; }
.avatar-crop-viewport img {
  position: absolute;
  max-width: none;
  object-fit: contain;
  transform: translate(-50%, -50%);
  pointer-events: none;
  user-select: none;
}
.avatar-zoom-row {
  display: grid;
  grid-template-columns: 20px 1fr 20px;
  gap: .65rem;
  align-items: center;
  margin-top: 1rem;
  color: #a1a1aa;
  text-align: center;
}
.avatar-zoom-row input { width: 100%; accent-color: #f43f5e; }
</style>
