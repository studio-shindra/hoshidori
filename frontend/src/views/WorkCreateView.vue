<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconPlus, IconX, IconSearch } from '@tabler/icons-vue'
import TheaterPicker from '@/components/TheaterPicker.vue'

const router = useRouter()
const route = useRoute()
const title = ref(route.query.title || '')
const description = ref('')
const companyName = ref('')
const castList = ref([])
const theaters = ref([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const showOptionalDetails = ref(false)
const duplicateWork = ref(null)

// 公演（劇場+日程）リスト — 複数追加可能
const perfEntries = ref([{ theater: '', startDate: '', endDate: '' }])

function addPerfEntry() {
  perfEntries.value.push({ theater: '', startDate: '', endDate: '' })
}

function removePerfEntry(index) {
  perfEntries.value.splice(index, 1)
}

function addTheaterOption(theater) {
  if (!theaters.value.some((item) => item.id === theater.id)) {
    theaters.value.push(theater)
    theaters.value.sort((a, b) => a.name.localeCompare(b.name, 'ja'))
  }
}

// 出演者・スタッフ検索
const castInput = ref('')
const castSuggestions = ref([])
const castSearching = ref(false)
const showCastDropdown = ref(false)
let castSearchTimer = null

watch(castInput, (val) => {
  clearTimeout(castSearchTimer)
  const q = val.trim()
  if (q.length < 1) {
    castSuggestions.value = []
    showCastDropdown.value = false
    return
  }
  castSearchTimer = setTimeout(async () => {
    castSearching.value = true
    try {
      const data = await api.get(`/api/people/?q=${encodeURIComponent(q)}`)
      const results = data.results || data
      // 既に追加済みを除外
      const added = new Set(castList.value.map(c => c.name))
      castSuggestions.value = results.filter(p => !added.has(p.name))
      showCastDropdown.value = true
    } catch {
      castSuggestions.value = []
    } finally {
      castSearching.value = false
    }
  }, 300)
})

function selectCast(person) {
  if (castList.value.some(c => c.name === person.name)) return
  castList.value.push({ name: person.name, id: person.id })
  castInput.value = ''
  showCastDropdown.value = false
}

function addNewCast() {
  const name = castInput.value.trim()
  if (!name) return
  if (castList.value.some(c => c.name === name)) return
  castList.value.push({ name, isNew: true })
  castInput.value = ''
  showCastDropdown.value = false
}

function removeCast(index) {
  castList.value.splice(index, 1)
}

function onCastKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault()
    // サジェストがあれば最初を選択、なければ新規追加
    if (castSuggestions.value.length) {
      selectCast(castSuggestions.value[0])
    } else {
      addNewCast()
    }
  }
}

function onCastBlur() {
  // ドロップダウンクリックより先に閉じないよう少し遅延
  setTimeout(() => { showCastDropdown.value = false }, 200)
}

onMounted(async () => {
  try {
    const data = await api.get('/api/theaters/')
    theaters.value = data.results || data
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!title.value.trim()) return
  const validEntries = perfEntries.value.filter(e => e.theater)
  if (!validEntries.length) {
    error.value = '劇場を選んでください'
    return
  }
  submitting.value = true
  error.value = ''
  duplicateWork.value = null
  try {
    const existingData = await api.getFresh(`/api/works/?q=${encodeURIComponent(title.value.trim())}`)
    const existingWorks = existingData.results || existingData
    const normalizedTitle = title.value.trim().normalize('NFKC').toLocaleLowerCase('ja')
    const existing = existingWorks.find((item) => item.title.trim().normalize('NFKC').toLocaleLowerCase('ja') === normalizedTitle)
    if (existing) {
      duplicateWork.value = existing
      error.value = '同じタイトルの作品がすでに登録されています'
      return
    }
    const work = await api.post('/api/works/', {
      title: title.value.trim(),
      description: description.value.trim(),
    })

    // 各劇場ごとに公演を作成
    let firstPerformanceId = null
    for (const entry of validEntries) {
      const perf = await api.post('/api/performances/', {
        work: work.id,
        theater: Number(entry.theater),
        company_name: companyName.value.trim(),
        start_date: entry.startDate || null,
        end_date: entry.endDate || null,
      })
      if (!firstPerformanceId) firstPerformanceId = perf.id

      // キャスト追加（最初の公演にだけ紐づけ）
      if (entry === validEntries[0]) {
        for (const cast of castList.value) {
          await api.post(`/api/performances/${perf.id}/add_cast/`, {
            name: cast.name,
          })
        }
      }
    }

    if (route.query.next === '/logs/new' && firstPerformanceId) {
      router.push({ path: '/logs/new', query: { performance: firstPerformanceId } })
    } else {
      router.push(`/works/${work.slug}`)
    }
  } catch (e) {
    error.value = e.data ? Object.values(e.data).flat().join(' ') : '作成に失敗しました'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center justify-content-between pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0 small text-decoration-none page-back" @click="router.back()">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </button>
      <h1 class="fs-6 fw-bold mb-0">作品を登録</h1>
      <div class="page-back-spacer"></div>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <form v-else @submit.prevent="submit" class="px-3 d-flex flex-column gap-3">
      <div class="quick-create-note">
        <strong>まずは作品名と劇場だけで登録できます。</strong>
        <span>足りない情報は、あとからみんなで編集できます。</span>
      </div>
      <div>
        <label class="form-label tiny text-secondary">タイトル *</label>
        <input
          v-model="title"
          type="text"
          required
          placeholder="作品タイトル"
          class="form-control bg-dark border-secondary text-light"
        />
      </div>
      <!-- 公演エントリ（複数追加可能） -->
      <div v-for="(entry, ei) in perfEntries" v-show="ei === 0 || showOptionalDetails" :key="ei" class="perf-entry" :class="{ 'primary-entry': ei === 0 }">
        <div v-if="ei > 0" class="d-flex align-items-center justify-content-between mb-2">
          <span class="tiny text-secondary fw-bold">公演 {{ ei + 1 }}</span>
          <button type="button" class="btn-icon-sm" @click="removePerfEntry(ei)">
            <IconX :size="14" />
          </button>
        </div>
        <div class="d-flex flex-column gap-2">
          <div>
            <label class="form-label tiny text-secondary">劇場{{ ei === 0 ? ' *' : '' }}</label>
            <TheaterPicker
              v-model="entry.theater"
              :theaters="theaters"
              @theater-created="addTheaterOption"
            />
          </div>
          <div v-if="showOptionalDetails" class="row g-2">
            <div class="col-6">
              <label class="form-label tiny text-secondary">開始日（任意）</label>
              <input v-model="entry.startDate" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
            <div class="col-6">
              <label class="form-label tiny text-secondary">終了日（任意）</label>
              <input v-model="entry.endDate" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
          </div>
        </div>
      </div>

      <button v-if="!showOptionalDetails" type="button" class="optional-toggle" @click="showOptionalDetails = true">
        詳しい情報も追加する
      </button>

      <template v-if="showOptionalDetails">
      <button type="button" class="btn btn-outline-secondary btn-sm align-self-start" @click="addPerfEntry">
        <IconPlus :size="14" class="me-1" />別の公演を追加（地方公演など）
      </button>

      <div>
        <label class="form-label tiny text-secondary">説明（任意）</label>
        <textarea
          v-model="description"
          rows="2"
          placeholder="作品の説明"
          class="form-control bg-dark border-secondary text-light"
        ></textarea>
      </div>

      <div>
        <label class="form-label tiny text-secondary">カンパニー名（任意）</label>
        <input v-model="companyName" type="text" placeholder="劇団名など" class="form-control bg-dark border-secondary text-light" />
      </div>

      <!-- 出演者・スタッフ（検索 + 新規登録） -->
      <div>
        <label class="form-label tiny text-secondary">出演者・スタッフ</label>
        <div class="position-relative">
          <div class="d-flex align-items-center gap-0 position-relative">
            <IconSearch :size="14" class="cast-search-icon" />
            <input
              v-model="castInput"
              type="text"
              placeholder="名前で検索..."
              class="form-control bg-dark border-secondary text-light cast-search-input"
              @keydown="onCastKeydown"
              @focus="castInput.trim() && (showCastDropdown = true)"
              @blur="onCastBlur"
            />
          </div>
          <!-- サジェストドロップダウン -->
          <div v-if="showCastDropdown && castInput.trim()" class="cast-dropdown">
            <div v-if="castSearching" class="cast-dropdown-item text-secondary">検索中...</div>
            <template v-else>
              <button
                v-for="p in castSuggestions"
                :key="p.id"
                type="button"
                class="cast-dropdown-item"
                @mousedown.prevent="selectCast(p)"
              >
                {{ p.name }}
              </button>
              <button
                type="button"
                class="cast-dropdown-item cast-dropdown-new"
                @mousedown.prevent="addNewCast"
              >
                <IconPlus :size="12" class="me-1" />「{{ castInput.trim() }}」を新規登録
              </button>
            </template>
          </div>
        </div>
        <div v-if="castList.length" class="d-flex flex-wrap gap-1 mt-2">
          <span v-for="(c, i) in castList" :key="i" class="cast-pill">
            {{ c.name }}
            <button type="button" class="cast-pill-remove" @click="removeCast(i)">
              <IconX :size="10" />
            </button>
          </span>
        </div>
      </div>
      </template>

      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <RouterLink v-if="duplicateWork" :to="`/works/${duplicateWork.slug}`" class="btn btn-outline-light btn-sm">
        登録済みの「{{ duplicateWork.title }}」を見る
      </RouterLink>
      <button type="submit" :disabled="submitting || !title.trim() || !perfEntries[0].theater" class="btn btn-primary-rose w-100 fw-medium py-2">
        {{ submitting ? '作成中...' : (route.query.next === '/logs/new' ? '登録して記録へ' : '作品を登録') }}
      </button>
      <p class="tiny text-secondary text-center mb-4">未入力の情報は、作品ページからいつでも追加できます。</p>
    </form>
  </div>
</template>

<style scoped>
.quick-create-note { display: flex; flex-direction: column; gap: .25rem; padding: .85rem 1rem; border-radius: 12px; background: rgba(255,255,255,.045); }
.quick-create-note strong { color: #e4e4e7; font-size: .78rem; }
.quick-create-note span { color: #71717a; font-size: .67rem; }
.perf-entry {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0.75rem;
}
.perf-entry.primary-entry { padding: 0; border: 0; background: transparent; }
.optional-toggle { align-self: flex-start; padding: .25rem 0; border: 0; background: transparent; color: #a1a1aa; font-size: .72rem; text-decoration: underline; text-underline-offset: 3px; }
.btn-icon-sm {
  background: none;
  border: none;
  color: #a1a1aa;
  padding: 0.15rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.btn-icon-sm:hover {
  color: #f43f5e;
}
.cast-search-icon {
  position: absolute;
  left: 0.75rem;
  color: #a1a1aa;
  z-index: 1;
  pointer-events: none;
}
.cast-search-input {
  padding-left: 2rem;
}
.cast-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #1c1c1e;
  border: 1px solid #3f3f46;
  border-radius: 8px;
  margin-top: 4px;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}
.cast-dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  color: #e4e4e7;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.cast-dropdown-item:hover {
  background: rgba(255, 255, 255, 0.08);
}
.cast-dropdown-new {
  color: #f43f5e;
  border-top: 1px solid #3f3f46;
  display: flex;
  align-items: center;
}
.cast-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.1);
  color: #e4e4e7;
}
.cast-pill-remove {
  background: none;
  border: none;
  color: #a1a1aa;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.cast-pill-remove:hover {
  color: #f43f5e;
}
</style>
