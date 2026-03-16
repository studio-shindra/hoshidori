<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import { IconArrowLeft, IconX, IconPlus } from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()

const work = ref(null)
const performances = ref([])
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)

// perfId -> { query, suggestions, adding }
const castInputs = ref({})

async function fetchData() {
  loading.value = true
  try {
    const slug = route.params.slug
    work.value = await api.get(`/api/works/${slug}/`)
    const perfData = await api.get(`/api/performances/?work=${work.value.id}`)
    performances.value = perfData.results || perfData
    for (const p of performances.value) {
      castInputs.value[p.id] = { query: '', suggestions: [], adding: false }
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

async function saveWork() {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = false
  try {
    await api.patch(`/api/works/${route.params.slug}/`, {
      title: work.value.title,
      description: work.value.description,
    })
    saveSuccess.value = true
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
      <button class="btn btn-link text-secondary p-0" @click="router.back()">
        <IconArrowLeft :size="16" />
      </button>
      <h1 class="fs-6 fw-bold mb-0">作品を編集</h1>
      <div style="width: 32px"></div>
    </header>

    <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
    <template v-else-if="work">

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
        <p v-if="saveSuccess" class="small color-green mb-0">保存しました</p>
        <button :disabled="saving" class="btn btn-primary-rose fw-medium" @click="saveWork">
          {{ saving ? '保存中...' : '情報を保存' }}
        </button>
      </div>

      <!-- Performances & Cast -->
      <div class="px-3 d-flex flex-column gap-3 mb-5">
        <h2 class="fw-bold fs-2 mb-0">Cast</h2>

        <div v-if="!performances.length" class="text-center py-3">
          <p class="text-secondary small mb-2">公演がまだ登録されていません</p>
          <RouterLink to="/performances/new" class="btn btn-outline-secondary btn-sm">公演を追加</RouterLink>
        </div>

        <div v-for="perf in performances" :key="perf.id" class="card bg-dark border-0 p-3">
          <div class="small fw-semibold mb-1">{{ perf.theater_name }}</div>
          <div class="tiny text-secondary mb-3">{{ perf.start_date }}〜{{ perf.end_date }}</div>

          <!-- Cast tags -->
          <div class="d-flex flex-wrap gap-2 mb-3">
            <span
              v-for="cast in perf.casts"
              :key="cast.id"
              class="cast-tag"
            >
              {{ cast.person_name }}
              <span v-if="cast.role_name" class="cast-role"> · {{ cast.role_name }}</span>
              <button class="cast-remove" @click="removeCast(perf.id, cast.id)">
                <IconX :size="10" />
              </button>
            </span>
            <span v-if="!perf.casts.length" class="tiny text-secondary">キャスト未登録</span>
          </div>

          <!-- Add cast -->
          <div class="position-relative">
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
      </div>

    </template>
  </div>
</template>

<style scoped>
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
