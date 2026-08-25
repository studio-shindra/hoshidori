<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconX, IconPlus } from '@tabler/icons-vue'
import { useAuthStore } from '@/stores/auth'
import TheaterPicker from '@/components/TheaterPicker.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const work = ref(null)
const performances = ref([])
const theaters = ref([])
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref('')
const showAddPerformance = ref(false)
const addingPerformance = ref(false)
const addPerformanceError = ref('')
const newPerformance = ref({ theater: '', company_name: '', start_date: '', end_date: '' })

// perfId -> { query, suggestions, adding }
const castInputs = ref({})
const isWorkOwner = computed(() => auth.user?.username === work.value?.created_by)
const isPerformanceOwner = (performance) => auth.user?.username === performance.created_by

function addTheaterOption(theater) {
  if (!theaters.value.some((item) => item.id === theater.id)) {
    theaters.value.push(theater)
    theaters.value.sort((a, b) => a.name.localeCompare(b.name, 'ja'))
  }
}

async function fetchData() {
  loading.value = true
  try {
    const slug = route.params.slug
    work.value = await api.get(`/api/works/${slug}/`)
    const [perfData, theaterData] = await Promise.all([
      api.get(`/api/performances/?work=${work.value.id}`),
      api.get('/api/theaters/'),
    ])
    performances.value = perfData.results || perfData
    theaters.value = theaterData.results || theaterData
    for (const p of performances.value) {
      castInputs.value[p.id] = { query: '', suggestions: [], adding: false }
    }
  } catch (error) {
    if (error.status === 404) router.replace({ name: 'not-found' })
  } finally {
    loading.value = false
  }
}

async function savePerformance(performance) {
  performance.saving = true
  performance.saveError = ''
  performance.saveSuccess = ''
  try {
    const body = {
      theater: Number(performance.theater),
      company_name: performance.company_name || '',
      start_date: performance.start_date || null,
      end_date: performance.end_date || null,
    }
    if (isPerformanceOwner(performance)) {
      await api.patch(`/api/performances/${performance.id}/`, body)
      performance.theater_name = theaters.value.find((theater) => theater.id === Number(performance.theater))?.name || performance.theater_name
      performance.saveSuccess = '保存しました'
    } else {
      await api.post(`/api/performances/${performance.id}/propose-edit/`, body)
      performance.saveSuccess = '修正案を送りました。確認後に反映されます'
    }
  } catch (e) {
    performance.saveError = e.data ? Object.values(e.data).flat().join(' ') : '公演情報の保存に失敗しました'
  } finally {
    performance.saving = false
  }
}

async function addPerformance() {
  if (!newPerformance.value.theater) return
  addingPerformance.value = true
  addPerformanceError.value = ''
  try {
    const created = await api.post('/api/performances/', {
      work: work.value.id,
      theater: Number(newPerformance.value.theater),
      company_name: newPerformance.value.company_name || '',
      start_date: newPerformance.value.start_date || null,
      end_date: newPerformance.value.end_date || null,
    })
    created.casts ||= []
    performances.value.push(created)
    castInputs.value[created.id] = { query: '', suggestions: [], adding: false }
    newPerformance.value = { theater: '', company_name: '', start_date: '', end_date: '' }
    showAddPerformance.value = false
  } catch (e) {
    addPerformanceError.value = e.data ? Object.values(e.data).flat().join(' ') : '公演の追加に失敗しました'
  } finally {
    addingPerformance.value = false
  }
}

onMounted(fetchData)

async function saveWork() {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const body = {
      title: work.value.title,
      description: work.value.description,
    }
    if (isWorkOwner.value) {
      await api.patch(`/api/works/${route.params.slug}/`, body)
      saveSuccess.value = '保存しました'
    } else {
      await api.post(`/api/works/${route.params.slug}/propose-edit/`, body)
      saveSuccess.value = '修正案を送りました。確認後に反映されます'
    }
  } catch (e) {
    saveError.value = e.data ? Object.values(e.data).flat().join(' ') : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function searchPeople(perfId) {
  const state = castInputs.value[perfId]
  const q = state.query.trim()
  if (q.length < 1) {
    state.suggestions = []
    return
  }
  try {
    const data = await api.get(`/api/people/?q=${encodeURIComponent(q)}`)
    state.suggestions = (data.results || data).slice(0, 6)
  } catch {
    state.suggestions = []
  }
}

async function addCast(perfId, name) {
  name = name.trim()
  if (!name) return
  const state = castInputs.value[perfId]
  state.adding = true
  try {
    const cast = await api.post(`/api/performances/${perfId}/add_cast/`, { name })
    const perf = performances.value.find(p => p.id === perfId)
    if (perf && !perf.casts.some(c => c.id === cast.id)) {
      perf.casts.push(cast)
    }
    state.query = ''
    state.suggestions = []
  } catch {
    /* empty */
  } finally {
    state.adding = false
  }
}

async function removeCast(perfId, castId) {
  try {
    await api.delete(`/api/casts/${castId}/`)
    const perf = performances.value.find(p => p.id === perfId)
    if (perf) perf.casts = perf.casts.filter(c => c.id !== castId)
  } catch {
    /* empty */
  }
}

function onCastKeydown(e, perfId) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addCast(perfId, castInputs.value[perfId].query)
  }
}

function closeSuggestions(perfId) {
  setTimeout(() => {
    castInputs.value[perfId].suggestions = []
  }, 150)
}
</script>

<template>
  <div>
    <header class="d-flex align-items-center justify-content-between pt-4 pb-3">
      <button class="btn btn-link text-secondary p-0 small text-decoration-none page-back" @click="router.back()">
        <IconArrowLeft :size="16" class="me-1" />戻る
      </button>
      <h1 class="fs-6 fw-bold mb-0">作品を編集</h1>
      <div class="page-back-spacer"></div>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="work">

      <p v-if="!isWorkOwner" class="proposal-note mx-3 mb-4">このページはみんなで育てる作品情報です。修正内容は確認後に反映されます。</p>

      <!-- Work info -->
      <div class="px-3 d-flex flex-column gap-3 mb-5">
        <div>
          <label class="form-label tiny text-secondary">タイトル</label>
          <input v-model="work.title" type="text" class="form-control bg-dark border-secondary text-light" />
        </div>
        <div>
          <label class="form-label tiny text-secondary">説明</label>
          <textarea v-model="work.description" rows="3" placeholder="作品の説明（任意）" class="form-control bg-dark border-secondary text-light"></textarea>
        </div>
        <p v-if="saveError" class="small text-danger mb-0">{{ saveError }}</p>
        <p v-if="saveSuccess" class="small color-green mb-0">{{ saveSuccess }}</p>
        <button :disabled="saving" class="btn btn-primary-rose fw-medium" @click="saveWork">
          {{ saving ? '保存中...' : '情報を保存' }}
        </button>
      </div>

      <!-- Performances & Cast -->
      <div class="px-3 d-flex flex-column gap-3 mb-5">
        <h2 class="fw-bold fs-5 mb-0">公演情報</h2>

        <div v-if="!performances.length" class="text-center py-3">
          <p class="text-secondary small mb-2">公演がまだ登録されていません</p>
        </div>

        <div v-for="perf in performances" :key="perf.id" class="card bg-dark border-0 p-3 d-flex flex-column gap-3">
          <div>
            <label class="form-label tiny text-secondary">劇場 *</label>
            <TheaterPicker
              v-model="perf.theater"
              :theaters="theaters"
              @theater-created="addTheaterOption"
            />
          </div>
          <div class="row g-2">
            <div class="col-6">
              <label class="form-label tiny text-secondary">開始日</label>
              <input v-model="perf.start_date" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
            <div class="col-6">
              <label class="form-label tiny text-secondary">終了日</label>
              <input v-model="perf.end_date" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
          </div>
          <div>
            <label class="form-label tiny text-secondary">団体名</label>
            <input v-model="perf.company_name" type="text" placeholder="未入力" class="form-control form-control-sm bg-dark border-secondary text-light" />
          </div>

          <button class="btn btn-outline-secondary btn-sm align-self-start" :disabled="perf.saving || !perf.theater" @click="savePerformance(perf)">
            {{ perf.saving ? '保存中...' : '公演情報を保存' }}
          </button>
          <p v-if="perf.saveError" class="small text-danger mb-0">{{ perf.saveError }}</p>
          <p v-if="perf.saveSuccess" class="small color-green mb-0">{{ perf.saveSuccess }}</p>

          <h3 class="tiny text-secondary fw-bold mb-0">出演者・スタッフ</h3>

          <!-- Cast tags -->
          <div class="d-flex flex-wrap gap-2">
            <span
              v-for="cast in perf.casts"
              :key="cast.id"
              class="cast-tag"
            >
              {{ cast.person_name }}
              <span v-if="cast.role_name" class="cast-role"> · {{ cast.role_name }}</span>
              <button v-if="isPerformanceOwner(perf)" class="cast-remove" :aria-label="`${cast.person_name}を出演者から外す`" @click="removeCast(perf.id, cast.id)">
                <IconX :size="10" />
              </button>
            </span>
            <span v-if="!perf.casts.length" class="tiny text-secondary">キャスト未登録</span>
          </div>

          <!-- Add cast -->
          <div v-if="isPerformanceOwner(perf)" class="position-relative">
            <div class="d-flex gap-2">
              <input
                v-model="castInputs[perf.id].query"
                type="text"
                placeholder="俳優名を入力 → Enter で追加"
                class="form-control bg-dark border-secondary text-light form-control-sm"
                @input="searchPeople(perf.id)"
                @keydown="onCastKeydown($event, perf.id)"
                @blur="closeSuggestions(perf.id)"
              />
              <button
                class="btn btn-dark btn-sm px-3"
                aria-label="出演者を追加"
                :disabled="!castInputs[perf.id].query.trim() || castInputs[perf.id].adding"
                @click="addCast(perf.id, castInputs[perf.id].query)"
              >
                <IconPlus :size="14" />
              </button>
            </div>
            <!-- Suggestions -->
            <div v-if="castInputs[perf.id].suggestions.length" class="suggestions">
              <button
                v-for="p in castInputs[perf.id].suggestions"
                :key="p.id"
                class="suggestion-item"
                @mousedown.prevent="addCast(perf.id, p.name)"
              >
                {{ p.name }}
              </button>
            </div>
          </div>
        </div>

        <button v-if="!showAddPerformance" class="btn btn-outline-secondary btn-sm align-self-start" @click="showAddPerformance = true">
          <IconPlus :size="14" class="me-1" />別の公演を追加
        </button>

        <div v-else class="card bg-dark border-0 p-3 d-flex flex-column gap-3">
          <div class="d-flex align-items-center justify-content-between">
            <h3 class="small fw-bold mb-0">公演を追加</h3>
            <button class="btn btn-link p-0 text-secondary" aria-label="公演追加を閉じる" @click="showAddPerformance = false"><IconX :size="17" /></button>
          </div>
          <div>
            <label class="form-label tiny text-secondary">劇場 *</label>
            <TheaterPicker
              v-model="newPerformance.theater"
              :theaters="theaters"
              @theater-created="addTheaterOption"
            />
          </div>
          <div>
            <label class="form-label tiny text-secondary">団体名</label>
            <input v-model="newPerformance.company_name" type="text" placeholder="未入力でも登録できます" class="form-control form-control-sm bg-dark border-secondary text-light" />
          </div>
          <div class="row g-2">
            <div class="col-6">
              <label class="form-label tiny text-secondary">開始日</label>
              <input v-model="newPerformance.start_date" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
            <div class="col-6">
              <label class="form-label tiny text-secondary">終了日</label>
              <input v-model="newPerformance.end_date" type="date" class="form-control form-control-sm bg-dark border-secondary text-light" />
            </div>
          </div>
          <p class="tiny text-secondary mb-0">日付と団体名は、わかる人があとから編集できます。</p>
          <p v-if="addPerformanceError" class="small text-danger mb-0">{{ addPerformanceError }}</p>
          <button class="btn btn-primary-rose btn-sm" :disabled="addingPerformance || !newPerformance.theater" @click="addPerformance">
            {{ addingPerformance ? '追加中...' : 'この公演を追加' }}
          </button>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
.proposal-note { padding: .75rem .9rem; border: 1px solid rgba(251,191,36,.2); border-radius: 10px; background: rgba(251,191,36,.06); color: #d4d4d8; font-size: .72rem; line-height: 1.65; }
.cast-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(255, 255, 255, 0.08);
  color: #e4e4e7;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem 0.25rem 0.75rem;
  border-radius: 99px;
}
.cast-role {
  color: #71717a;
  font-size: 0.65rem;
}
.cast-remove {
  background: none;
  border: none;
  color: #71717a;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  line-height: 1;
  &:hover { color: #f43f5e; }
}
.suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 40px;
  background: #18181b;
  border: 1px solid #3f3f46;
  border-radius: 6px;
  z-index: 100;
  overflow: hidden;
}
.suggestion-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #27272a;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  color: #e4e4e7;
  cursor: pointer;
  &:last-child { border-bottom: none; }
  &:hover { background: rgba(255, 255, 255, 0.05); }
}
</style>
