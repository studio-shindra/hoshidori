<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { IconCirclePlus, IconStar, IconBinoculars } from '@tabler/icons-vue'
import { fetchMyLogs, deleteLog as apiDeleteLog } from '@/apiClient'
import { currentUser } from '@/authState'
import { listLocalLogs, deleteLocalLog, isGuestUser } from '@/lib/localLogs'
import SimpleSpinner from '@/components/LoadingSimpleSpinner.vue'

const logs = ref([])
const loading = ref(true)
const error = ref(null)
const showFilter = ref(false)
const keyword = ref('')
const startDate = ref('')
const endDate = ref('')
const tagQuery = ref('')
const selectedTags = ref([])
const selectedActors = ref([])
const selectedTheaters = ref([])
const router = useRouter()
const isGuest = computed(() => isGuestUser() || !currentUser.value)

function clearFilters() {
  keyword.value = ''
  tagQuery.value = ''
  startDate.value = ''
  endDate.value = ''
  selectedTags.value = []
  selectedActors.value = []
  selectedTheaters.value = []
}

const filteredLogs = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  const tagKw = tagQuery.value.trim().toLowerCase()

  return logs.value.filter((log) => {
    const watched = log.watchedDate || log.watched_at
    const watchedDay = watched ? new Date(watched) : null

    const logTags = [
      ...(Array.isArray(log.tags) ? log.tags : []),
      ...(Array.isArray(log.work?.tags) ? log.work.tags : []),
    ].map((t) => String(t).toLowerCase())
    const actorNames = Array.isArray(log.work?.actors)
      ? log.work.actors
          .map((a) => {
            if (typeof a === 'object' && a !== null) {
              return String(a.name || '').toLowerCase()
            }
            return String(a).toLowerCase()
          })
          .filter(Boolean)
      : []
    const theaterName = log.work?.main_theater?.name ? String(log.work.main_theater.name).toLowerCase() : ''

    if (startDate.value) {
      const from = new Date(startDate.value)
      if (watchedDay && watchedDay < from) return false
    }
    if (endDate.value) {
      const to = new Date(endDate.value)
      if (watchedDay && watchedDay > to) return false
    }

    if (tagKw) {
      const hasTag = logTags.some((t) => t.includes(tagKw))
      if (!hasTag) return false
    }

    if (selectedTags.value.length) {
      const hasAll = selectedTags.value.every((t) => logTags.includes(String(t).toLowerCase()))
      if (!hasAll) return false
    }

    if (selectedActors.value.length) {
      const hasAllActors = selectedActors.value.every((a) => actorNames.includes(String(a).toLowerCase()))
      if (!hasAllActors) return false
    }

    if (selectedTheaters.value.length) {
      const hasTheater = selectedTheaters.value.some((th) => theaterName === String(th).toLowerCase())
      if (!hasTheater) return false
    }

    if (kw) {
      const title = log.work?.title || ''
      const memo = log.memo || ''
      const troupe = log.work?.troupe?.name || ''
      const hit = [title, memo, troupe]
        .map((v) => String(v).toLowerCase())
        .some((v) => v.includes(kw))
      if (!hit) return false
    }

    return true
  })
})

const availableTags = computed(() => {
  const set = new Set()
  logs.value.forEach((log) => {
    const candidates = [
      ...(Array.isArray(log.tags) ? log.tags : []),
      ...(Array.isArray(log.work?.tags) ? log.work.tags : []),
    ]
    candidates.forEach((t) => {
      const name = String(t).trim()
      if (name) set.add(name)
    })
  })
  return Array.from(set).sort()
})

const availableActors = computed(() => {
  const set = new Set()
  logs.value.forEach((log) => {
    const names = Array.isArray(log.work?.actors) ? log.work.actors : []
    names.forEach((n) => {
      const name = typeof n === 'object' ? String(n.name || '').trim() : String(n || '').trim()
      if (name) set.add(name)
    })
  })
  return Array.from(set).sort()
})

const availableTheaters = computed(() => {
  const set = new Set()
  logs.value.forEach((log) => {
    const name = log.work?.main_theater?.name
    if (name) set.add(String(name).trim())
  })
  return Array.from(set).sort()
})

async function fetchLogs({ force = false } = {}) {
  // キャッシュ表示がある場合は「読み込み中…」は出さない
  if (!logs.value.length) {
    loading.value = true
  }
  error.value = null

  try {
    if (isGuest.value) {
      logs.value = listLocalLogs()
    } else {
      const data = await fetchMyLogs({ force })
      logs.value = data
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 俳優などの新フィールド反映のため初回は強制取得
onMounted(() => fetchLogs({ force: true }))

function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

async function deleteLog(id) {
  const ok = window.confirm('この観劇ログを削除しますか？')
  if (!ok) return

  try {
    if (isGuest.value) {
      deleteLocalLog(id)
      logs.value = listLocalLogs()
    } else {
      await apiDeleteLog(id)
      // 強制で取り直す（キャッシュ無視）
      await fetchLogs({ force: true })
    }
  } catch (e) {
    alert('削除に失敗しました。もう一度お試しください。')
  }
}
</script>

<template>
  <main class="container py-4">
    <!-- <h1 class="mb-3 df-center">
      <img 
        src="/icon.svg"
        style="width: 80px;"
        alt="">
    </h1> -->

    
    <!-- <router-link to="/logs/new" class="btn text-dark df-center my-5">
      <IconCirclePlus :size="40"/>
    </router-link> -->

    <SimpleSpinner :show="loading && logs.length === 0" />
  
    <p v-if="error">エラー: {{ error }}</p>
    <div
      v-else-if="!loading && logs.length === 0"
      class="df-center"
      style="height: calc(100vh - 80px - 80px);"><!-- ヘッダーとフッターの高さを引く --> 
      <div class="df-center text-center flex-column">
        その体験は<br>
        あなたの人生を豊かにします<br>
        <router-link to="/logs/new" class="mt-3">
          観劇を記録する
        </router-link>
      </div>
      
    </div>

    <div v-else>

    <h1 class="mb-3 fs-3 fw-bold text-center">観劇リスト</h1>

    <div class="search row g-2 mb-3">
      <button class="btn btn-sm btn-outline-secondary" @click="showFilter = !showFilter">
        {{ showFilter ? '閉じる' : '絞り込み' }}
      </button>
      <div class="warp p-3 bg-light" v-show="showFilter"><!-- ここがアコーディオンで開く -->
        <div class="area d-flex flex-column gap-3 align-items-center">
          <div class="box w-100">
            <label class="mb-1">期間指定</label>
            <div class="d-flex gap-2">
              <input v-model="startDate" type="date" class="form-control form-control-sm" aria-label="開始日">
              <span>〜</span>
              <input v-model="endDate" type="date" class="form-control form-control-sm" aria-label="終了日">
            </div>
          </div>
          <div class="box w-100">
            <label class="mb-1">タグ</label>
            <div class="d-flex flex-wrap gap-2">
              <label
                v-for="tag in availableTags"
                :key="tag"
                :class="['badge filter-pill', selectedTags.includes(tag) ? 'selected' : '']"
              >
                <input type="checkbox" class="pill-check" :value="tag" v-model="selectedTags">
                {{ tag }}
              </label>
            </div>
          </div>
          <div class="box w-100">
            <label class="mb-1">俳優</label>
            <div class="d-flex flex-wrap gap-2">
              <label
                v-for="actor in availableActors"
                :key="actor"
                :class="['badge filter-pill', selectedActors.includes(actor) ? 'selected' : '']"
              >
                <input type="checkbox" class="pill-check" :value="actor" v-model="selectedActors">
                {{ actor }}
              </label>
            </div>
          </div>
          <div class="box w-100">
            <label class="mb-1">劇場</label>
            <div class="d-flex flex-wrap gap-2">
              <label
                v-for="theater in availableTheaters"
                :key="theater"
                :class="['badge filter-pill', selectedTheaters.includes(theater) ? 'selected' : '']"
              >
                <input type="checkbox" class="pill-check" :value="theater" v-model="selectedTheaters">
                {{ theater }}
              </label>
            </div>
          </div>
          <div class="box w-100">
            <label class="mb-1">キーワード</label>
            <input
              v-model="keyword"
              type="search"
              class="form-control form-control-sm"
              placeholder="作品名・劇団名・メモを検索"
            >
          </div>
          <div class="col-12 d-flex gap-2">
            <button class="btn btn-sm btn-primary" @click="showFilter = false">閉じる</button>
            <button class="btn btn-sm btn-outline-secondary" @click="clearFilters">クリア</button>
          </div>
        </div>
      </div>
    </div>

      <div class="row g-1">
        <!-- 新規登録 -->
        <div class="col-6 col-md-3 col-lg-2 df-center mb-2">
          <router-link
            to="/logs/new"
            class="poster position-relative d-flex align-items-center justify-content-center bg-light h-100 w-100"
            style="border: 2px dashed #ccc; cursor: pointer;"
          >
            <div class="text-center text-muted">
              <IconCirclePlus :size="40" />
            </div>
          </router-link>
        </div>
        <!-- ログら ここに検索結果 -->
        <div v-for="log in filteredLogs" :key="log.id" class="col-6 col-md-3 col-lg-2">
          <div class="poster position-relative">
            <router-link :to="`/logs/${log.id}/detail`">
              <img
                v-if="log.work?.main_image || log.work?.main_image_url"
                :src="log.work?.main_image || log.work?.main_image_url"
                class="poster-img w-100"
                :alt="log.work.title"
                style="aspect-ratio: 1/1.414; object-fit: cover; cursor: pointer;"
              >
              <div
                v-else
                class="poster-img bg-secondary d-flex align-items-center justify-content-center text-white"
                style="aspect-ratio: 1/1.414; cursor: pointer;"
              >
                画像なし
              </div>
            </router-link>
        
            <!-- 許諾申請中のオーバーレイ -->
            <div
              v-if="(log.work?.main_image || log.work?.main_image_url) && log.work?.troupe && !log.work.troupe.image_allowed"
              class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
              style="background-color: rgba(0, 0, 0, 0.8); z-index: 5; pointer-events: none;"
            >
              <div class="text-center text-white">
                <div style="font-size: 12px; font-weight: bold;">
                  {{ log.work.troupe?.name || '劇団' }}様に<br>許諾申請中
                </div>
              </div>
            </div>
          </div>
          <div class="poster-body df-center gap-2 bg-light p-1">
            <div class="star df-center text-muted gap-1">
              <IconStar :size="16" />
              <div>{{ log.rating }}</div>
            </div>
            <div class="date df-center"><IconBinoculars :size="20" /><small>{{ formatDate(log.watchedDate) }}</small></div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.filter-pill {
  border: 1px solid #ddd;
  background: #f8f9fa;
  color: #333;
  cursor: pointer;
  padding: 6px 10px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.filter-pill.selected {
  background: #0d6efd;
  color: #fff;
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.15);
}

.pill-check {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 0;
  height: 0;
}
</style>