<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '@/apiClient'
import Multiselect from '@vueform/multiselect'
import { IconMovie, IconMapPin, IconUsers, IconPhoto, IconTags, IconUserStar } from '@tabler/icons-vue'

const router = useRouter()

const theaters = ref([])
const troupes = ref([])
const actors = ref([])
const loading = ref(true)

const form = ref({
  title: '',
  theaterId: '',
  troupe: '',
  description: '',
  imageFile: null,
  tags: '',
  actorIds: [],  // 選択された俳優ID配列
  actorNames: [], // 新規入力された俳優名配列
})

const uploading = ref(false)
const error = ref(null)
const fileInputRef = ref(null)
const imagePreview = ref(null)

// 劇場オプション
const theaterOptions = computed(() =>
  theaters.value.map(t => ({
    value: t.id,
    label: `${t.name}（${t.area || ''}）`
  }))
)

// 劇団オプション
const troupeOptions = computed(() =>
  troupes.value.map(tp => ({
    value: tp.id,
    label: tp.name
  }))
)

// 俳優オプション（既存 + 新規入力可能）
const actorOptions = computed(() =>
  actors.value.map(a => ({
    value: a.id,
    label: a.name
  }))
)

async function fetchData() {
  loading.value = true
  try {
    const [theatersData, actorsData] = await Promise.all([
      request('/api/theaters/'),
      request('/api/actors/')
    ])
    theaters.value = theatersData
    actors.value = actorsData
    // 劇団は存在しない可能性もあるため個別フェッチ（失敗しても無視）
    try {
      const troupesData = await request('/api/troupes/')
      troupes.value = Array.isArray(troupesData) ? troupesData : []
    } catch (err) {
      troupes.value = []
    }
  } catch (e) {
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0] || null
  form.value.imageFile = file
  
  // プレビュー作成
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result
    }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
}

async function handleSubmit(e) {
  e.preventDefault()
  error.value = null
  uploading.value = true

  try {
    // 劇場の処理（新規作成または既存ID）
    let theaterIdToUse = null
    if (form.value.theaterId) {
      if (typeof form.value.theaterId === 'string') {
        // 新規劇場名として入力された場合
        const newTheater = await request('/api/theaters/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: form.value.theaterId })
        }).catch(() => null)
        theaterIdToUse = newTheater?.id || null
      } else {
        // 既存劇場IDが選択された場合
        theaterIdToUse = Number(form.value.theaterId)
      }
    }

    // 選択された俳優IDと新規入力された名前を処理
    const selectedActorIds = form.value.actorIds.filter(id => typeof id === 'number')
    const newActorNames = form.value.actorIds.filter(id => typeof id === 'string')
    
    // 新規俳優を作成
    const createdActors = await Promise.all(
      newActorNames.map(name =>
        request('/api/actors/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        }).catch(() => null) // 重複エラーは無視
      )
    )
    
    // 作成された俳優のIDを追加
    const allActorIds = [
      ...selectedActorIds,
      ...createdActors.filter(a => a?.id).map(a => a.id)
    ]

    // まずcreate_or_get APIで作品を作成または取得
    // troupeは既存選択（数値ID）なら名前に変換、文字列ならそのまま使用
    let troupeName = ''
    if (form.value.troupe) {
      if (typeof form.value.troupe === 'number') {
        const opt = troupeOptions.value.find(o => o.value === form.value.troupe)
        troupeName = opt?.label || ''
      } else if (typeof form.value.troupe === 'string') {
        troupeName = form.value.troupe
      }
    }

    const payload = {
      title: form.value.title,
      troupe: troupeName,
      main_theater_id: theaterIdToUse,
    }

    const created = await request('/api/works/create_or_get/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    // 画像と俳優がある場合は別途PATCH
    if (created?.id) {
      const fd = new FormData()
      if (form.value.imageFile) {
        fd.append('main_image', form.value.imageFile)
      }
      if (allActorIds.length > 0) {
        allActorIds.forEach(id => fd.append('actors', id))
      }
      
      if (form.value.imageFile || allActorIds.length > 0) {
        await request(`/api/works/${created.id}/`, {
          method: 'PATCH',
          body: fd,
        })
      }
    }

    // 作品作成 → ログ新規作成画面へ
    const workId = created?.id
    if (workId) {
      router.push(`/logs/new?work=${workId}`)
    } else {
      router.push('/logs/new')
    }
  } catch (e) {
    console.error(e)
    error.value = e.message
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <main class="container py-4 work-new-page">
    <h1 class="fw-bold text-center fs-5">作品を登録</h1>
    <p v-if="loading">データ読み込み中...</p>

    <form v-else @submit="handleSubmit" class="mb-4">
      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small must"><IconMovie />タイトル</label>
        </div>
        <div class="col-9">
          <input
            type="text"
            class="form-control"
            v-model="form.title"
            placeholder="省略せず正式タイトルを入力してください"
            required
          />
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconMapPin />劇場</label>
        </div>
        <div class="col-9">
          <Multiselect
            v-model="form.theaterId"
            :options="theaterOptions"
            :searchable="true"
            :close-on-select="true"
            :create-option="true"
            placeholder="劇場を選択または入力して登録..."
            :no-options-text="'見つかりません'"
          />
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconUsers />制作</label>
        </div>
        <div class="col-9">
          <Multiselect
            v-model="form.troupe"
            :options="troupeOptions"
            :searchable="true"
            :close-on-select="true"
            :create-option="true"
            placeholder="制作団体を選択または入力して登録..."
            :no-options-text="'見つかりません'"
          />
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconUserStar />出演者</label>
        </div>
        <div class="col-9">
          <Multiselect
            v-model="form.actorIds"
            :options="actorOptions"
            mode="tags"
            :searchable="true"
            :create-option="true"
            placeholder="出演者を選択または入力して登録..."
            :no-options-text="'見つかりません'"
          />
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconTags />タグ</label>
        </div>
        <div class="col-9">
          <input
            type="text"
            class="form-control"
            v-model="form.tags"
            placeholder="例: 会話劇, コメディ, 一人芝居"
          />
        </div>
      </div>

      <div class="mb-3">
        <textarea
          class="form-control"
          rows="3"
          v-model="form.description"
          placeholder="作品説明（任意）"
          style="min-height: 150px;"
        />
      </div>
      <div class="mb-5">
        <div class="image">
          <!-- 非表示のファイル入力 -->
          <input
            ref="fileInputRef"
            type="file"
            class="d-none"
            accept="image/*"
            @change="onFileChange"
          />
          
          <!-- 画像プレビューまたは仮画像 -->
          <div class="wrap df-center mb-3">
            <div 
              class="image-preview-container"
              style="width: 100%; height: 100%; border: 2px dashed #ccc; border-radius: 8px; overflow: hidden; background: #f8f9fa; cursor: pointer;"
              @click="triggerFileInput"
            >
              <img 
                v-if="imagePreview"
                :src="imagePreview" 
                alt="プレビュー"
                style="width: 100%; height: 100%; object-fit: cover;"
              />
              <div 
                v-else
                class="df-center flex-column h-100 text-muted py-5"
              >
                <IconPhoto :size="48" />
                <div class="mt-2 small">クリックして画像を選択</div>
              </div>
            </div>
          </div>
          <div
            class="text-muted text-center"
            style="font-size: 12px;">
            公式サイトにあるメインポスターの画像を入力してください。<br>制作団体の許諾を取れ次第、順次掲載します。
          </div>
          <div v-if="form.imageFile" class="mt-1 text-center small text-success">
            <strong>選択中:</strong> {{ form.imageFile.name }}
          </div>
        </div>
      </div>
      
      <button type="submit" class="btn btn-primary w-100" :disabled="uploading">
        {{ uploading ? '保存中…' : '作品を保存してログ追加へ' }}
      </button>
    </form>

    <p v-if="error" class="text-danger">エラー: {{ error }}</p>
  </main>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>