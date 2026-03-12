<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconCamera, IconMask, IconCheck } from '@tabler/icons-vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const route = useRoute()
const router = useRouter()
const work = ref(null)
const posters = ref([])
const loading = ref(true)
const selectedFile = ref(null)
const caption = ref('')
const preview = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref(false)
const uploadProgress = ref('')

const fileInput = ref(null)

onMounted(async () => {
  try {
    const slug = route.params.slug
    if (slug) {
      const [w, p] = await Promise.all([
        api.get(`/api/works/${slug}/`),
        api.get(`/api/works/${slug}/posters/`),
      ])
      work.value = w
      posters.value = Array.isArray(p) ? p : p.results || []
    }
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

function openFilePicker() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    uploadError.value = '画像ファイルを選択してください'
    return
  }
  if (file.size > MAX_FILE_SIZE) {
    uploadError.value = 'ファイルサイズは10MB以下にしてください'
    return
  }

  selectedFile.value = file
  preview.value = URL.createObjectURL(file)
  uploadSuccess.value = false
  uploadError.value = ''
}

async function submitPoster() {
  if (!selectedFile.value) return
  uploading.value = true
  uploadError.value = ''
  uploadProgress.value = 'Cloudinaryにアップロード中...'

  try {
    // Step 1: Upload to Cloudinary
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('upload_preset', UPLOAD_PRESET)

    const cloudRes = await fetch(
      `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
      { method: 'POST', body: fd }
    )
    if (!cloudRes.ok) {
      throw new Error('Cloudinaryへのアップロードに失敗しました')
    }
    const cloudData = await cloudRes.json()

    // Step 2: Save to backend
    uploadProgress.value = 'サーバーに保存中...'
    const result = await api.post(`/api/works/${route.params.slug}/posters/`, {
      image_url: cloudData.secure_url,
      image_public_id: cloudData.public_id,
      image_width: cloudData.width,
      image_height: cloudData.height,
      image_format: cloudData.format,
      caption: caption.value,
    })

    posters.value.unshift(result)
    uploadSuccess.value = true
    selectedFile.value = null
    preview.value = null
    caption.value = ''
  } catch (e) {
    uploadError.value = e.data
      ? Object.values(e.data).flat().join(' ')
      : e.message || 'アップロードに失敗しました'
  } finally {
    uploading.value = false
    uploadProgress.value = ''
  }
}

function posterImageSrc(p) {
  return p.image_url || p.image || ''
}

const selectedPoster = () => posters.value.find((p) => p.is_selected)
</script>

<template>
  <div>
    <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0 small text-decoration-none" @click="router.back()">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </button>
      <h1 class="fs-6 fw-bold mb-0">ポスター写真を投稿</h1>
      <div style="width: 48px"></div>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <div v-else class="px-3 d-flex flex-column gap-4">
      <!-- 対象作品 -->
      <div class="card bg-dark border-0 p-3">
        <div class="tiny text-secondary mb-1">対象作品</div>
        <div class="fw-medium">{{ work ? (work.title || work.name) : '—' }}</div>
        <div v-if="work && work.description" class="tiny text-secondary">{{ work.description }}</div>
      </div>

      <!-- 現在のトップ画像 -->
      <div>
        <label class="form-label tiny text-secondary">現在のトップ画像</label>
        <template v-if="selectedPoster()">
          <div class="poster-current overflow-hidden rounded-3">
            <img :src="posterImageSrc(selectedPoster())" class="w-100 h-100 object-fit-cover" />
          </div>
          <div class="tiny text-secondary mt-1">
            by {{ selectedPoster().user_display_name }}
          </div>
        </template>
        <div v-else class="poster-current poster-empty d-flex flex-column align-items-center justify-content-center gap-2">
          <IconMask :size="36" class="text-secondary" />
          <span class="small text-secondary">まだ画像がありません</span>
        </div>
      </div>

      <!-- アップロードエリア -->
      <div>
        <label class="form-label tiny text-secondary">新しい画像をアップロード</label>
        <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="onFileChange" />

        <div v-if="preview" class="mb-3">
          <img :src="preview" class="w-100 rounded-3" style="max-height: 300px; object-fit: cover" />
        </div>

        <div class="upload-area" role="button" @click="openFilePicker">
          <IconCamera :size="32" class="text-secondary" />
          <span class="small text-secondary">{{ selectedFile ? selectedFile.name : 'タップして写真を選択' }}</span>
        </div>

        <div class="mt-2">
          <input v-model="caption" type="text" placeholder="キャプション（任意）" class="form-control bg-dark border-secondary text-light form-control-sm" />
        </div>

        <div class="tiny text-secondary mt-2 lh-base">
          この画像は作品ページのトップ画像候補になります。投稿者名も表示されます。<br />
          対応形式: JPG, PNG, WebP（10MB以下）
        </div>
      </div>

      <!-- 結果メッセージ -->
      <div v-if="uploading" class="small text-secondary">{{ uploadProgress }}</div>
      <div v-if="uploadSuccess" class="d-flex align-items-center gap-2 color-green small">
        <IconCheck :size="16" />投稿しました！
      </div>
      <p v-if="uploadError" class="small text-danger mb-0">{{ uploadError }}</p>

      <!-- Button -->
      <div class="mb-4">
        <button
          class="btn btn-primary-rose w-100 fw-medium py-2"
          :disabled="!selectedFile || uploading"
          @click="submitPoster"
        >
          {{ uploading ? '送信中...' : '送信する' }}
        </button>
      </div>

      <!-- 投稿済みポスター一覧 -->
      <section v-if="posters.length" class="mb-5">
        <h3 class="small fw-semibold text-secondary mb-3">投稿済みポスター</h3>
        <div class="d-flex flex-column gap-3">
          <div v-for="p in posters" :key="p.id" class="card bg-dark border-0 overflow-hidden">
            <img :src="posterImageSrc(p)" class="w-100" style="max-height: 200px; object-fit: cover" />
            <div class="p-2">
              <div class="d-flex justify-content-between align-items-center">
                <span class="tiny text-secondary">by {{ p.user_display_name }}</span>
                <span v-if="p.is_selected" class="badge badge-green">選択中</span>
              </div>
              <div v-if="p.caption" class="tiny text-light mt-1">{{ p.caption }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.poster-current {
  width: 100%;
  aspect-ratio: 3 / 2;
  border-radius: 12px;
  overflow: hidden;
  padding: 12px;
}
.upload-area {
  width: 100%;
  height: 120px;
  border: 2px dashed #3f3f46;
  border-radius: 12px;
  background: #18181b;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}
.upload-area:hover {
  border-color: #52525b;
}
</style>
