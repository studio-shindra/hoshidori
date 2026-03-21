<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconPlus, IconX, IconSearch } from '@tabler/icons-vue'

const router = useRouter()
const title = ref('')
const description = ref('')
const companyName = ref('')
const castList = ref([])
const theaters = ref([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

// 公演（劇場+日程）リスト — 複数追加可能
const perfEntries = ref([{ theater: '', startDate: '', endDate: '' }])

function addPerfEntry() {
  perfEntries.value.push({ theater: '', startDate: '', endDate: '' })
}

function removePerfEntry(index) {
  perfEntries.value.splice(index, 1)
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
  submitting.value = true
  error.value = ''
  try {
    const work = await api.post('/api/works/', {
      title: title.value.trim(),
      description: description.value.trim(),
    })

    // 各劇場ごとに公演を作成
    const validEntries = perfEntries.value.filter(e => e.theater && e.startDate && e.endDate)
    for (const entry of validEntries) {
      const perf = await api.post('/api/performances/', {
        work: work.id,
        theater: Number(entry.theater),
        company_name: companyName.value.trim(),
        start_date: entry.startDate,
        end_date: entry.endDate,
      })

      // キャスト追加（最初の公演にだけ紐づけ）
      if (entry === validEntries[0]) {
        for (const cast of castList.value) {
          await api.post(`/api/performances/${perf.id}/add_cast/`, {
            name: cast.name,
          })
        }
      }
    }

    router.push(`/works/${work.slug}`)
  } catch (e) {
    error.value = e.data ? Object.values(e.data).flat().join(' ') : '作成に失敗しました'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center gap-2 pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">作品を登録</h1>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <form v-else @submit.prevent="submit" class="px-3 d-flex flex-column gap-3">
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
      <div>
        <label class="form-label tiny text-secondary">説明（任意）</label>
        <textarea
          v-model="description"
          rows="2"
          placeholder="作品の説明"
          class="form-control bg-dark border-secondary text-light"
        ></textarea>
      </div>

      <hr class="border-secondary my-1" />
      <p class="tiny text-secondary mb-0">公演情報（任意・あとから追加も可）</p>

      <!-- 公演エントリ（複数追加可能） -->
      <div v-for="(entry, ei) in perfEntries" :key="ei" class="perf-entry">
        <div class="d-flex align-items-center justify-content-between mb-2">
          <span class="tiny text-secondary fw-bold">公演 {{ ei + 1 }}</span>
          <button v-if="perfEntries.length > 1" type="button" class="btn-icon-sm" @click="removePerfEntry(ei)">
            <IconX :size="14" />
          </button>
        </div>
        <div class="d-flex flex-column gap-2">
          <div>
            <label class="form-label tiny text-secondary">劇場</label>
            <select v-model="entry.theater" class="form-select form-select-sm bg-dark border-secondary text-light">
              <option value="">未選択</option>
              <option v-for="t in theaters" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="row g-2">
            <div class="col-6">
              <label class="form-label tiny text-secondary">開始日</label>
              <input v-model="entry.startDate" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
            <div class="col-6">
              <label class="form-label tiny text-secondary">終了日</label>
              <input v-model="entry.endDate" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
          </div>
        </div>
      </div>
      <button type="button" class="btn btn-outline-secondary btn-sm align-self-start" @click="addPerfEntry">
        <IconPlus :size="14" class="me-1" />公演を追加（地方公演など）
      </button>

      <div>
        <label class="form-label tiny text-secondary">カンパニー名</label>
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

      <p v-if="error" class="small text-danger mb-0">{{ error }}</p>
      <button type="submit" :disabled="submitting || !title.trim()" class="btn btn-primary-rose w-100 fw-medium py-2">
        {{ submitting ? '作成中...' : '作品を登録' }}
      </button>
      <p class="tiny text-secondary mb-4">slug は自動生成されます。登録後に作品ページへ移動します。</p>
    </form>
  </div>
</template>

<style scoped>
.perf-entry {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0.75rem;
}
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
