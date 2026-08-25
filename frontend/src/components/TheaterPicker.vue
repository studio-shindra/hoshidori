<script setup>
import { computed, ref, watch } from 'vue'
import { IconCheck, IconLoader2, IconMapPin, IconPlus, IconSearch, IconX } from '@tabler/icons-vue'
import { api } from '@/lib/api'

const props = defineProps({
  modelValue: { type: [Number, String], default: '' },
  theaters: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'theater-created'])

const query = ref('')
const focused = ref(false)
const googleCandidates = ref([])
const remoteTheaters = ref([])
const searchingGoogle = ref(false)
const registering = ref(false)
const error = ref('')
const showManualForm = ref(false)
const manualAddress = ref('')
let searchTimer = null
let searchSequence = 0

const selectedTheater = computed(() => props.theaters.find(
  (theater) => Number(theater.id) === Number(props.modelValue),
))

const localMatches = computed(() => {
  const normalized = query.value.trim().normalize('NFKC').toLocaleLowerCase('ja')
  const merged = new Map(props.theaters.map((theater) => [theater.id, theater]))
  for (const theater of remoteTheaters.value) merged.set(theater.id, theater)
  const options = Array.from(merged.values())
  if (!normalized) return options.slice(0, 8)
  return options.filter((theater) => {
    const haystack = [theater.name, theater.area_name, theater.address]
      .filter(Boolean).join(' ').normalize('NFKC').toLocaleLowerCase('ja')
    return haystack.includes(normalized)
  }).slice(0, 8)
})

watch(
  () => [props.modelValue, props.theaters],
  () => {
    if (!focused.value) query.value = selectedTheater.value?.name || ''
  },
  { immediate: true, deep: true },
)

watch(query, (value) => {
  clearTimeout(searchTimer)
  googleCandidates.value = []
  remoteTheaters.value = []
  error.value = ''
  const normalized = value.trim()
  const sequence = ++searchSequence
  if (!normalized || selectedTheater.value?.name === normalized) return

  searchTimer = setTimeout(async () => {
    searchingGoogle.value = normalized.length >= 2
    try {
      const [localData, googleData] = await Promise.all([
        api.getFresh(`/api/theaters/?q=${encodeURIComponent(normalized)}`),
        normalized.length >= 2
          ? api.getFresh(`/api/theaters/candidates/?q=${encodeURIComponent(normalized)}`)
          : Promise.resolve([]),
      ])
      if (sequence === searchSequence) {
        remoteTheaters.value = localData.results || localData
        googleCandidates.value = googleData.results || googleData
      }
    } catch {
      if (sequence === searchSequence) {
        remoteTheaters.value = []
        googleCandidates.value = []
      }
    } finally {
      if (sequence === searchSequence) searchingGoogle.value = false
    }
  }, 350)
})

function handleInput() {
  if (selectedTheater.value && query.value !== selectedTheater.value.name) {
    emit('update:modelValue', '')
  }
  showManualForm.value = false
}

function chooseExisting(theater) {
  if (!props.theaters.some((item) => item.id === theater.id)) emit('theater-created', theater)
  emit('update:modelValue', theater.id)
  query.value = theater.name
  focused.value = false
  showManualForm.value = false
}

async function registerTheater(payload) {
  registering.value = true
  error.value = ''
  try {
    const theater = await api.post('/api/theaters/register/', payload)
    emit('theater-created', theater)
    emit('update:modelValue', theater.id)
    query.value = theater.name
    focused.value = false
    showManualForm.value = false
    manualAddress.value = ''
  } catch (requestError) {
    error.value = requestError.data
      ? Object.values(requestError.data).flat().join(' ')
      : '劇場を登録できませんでした'
  } finally {
    registering.value = false
  }
}

function chooseGoogle(candidate) {
  registerTheater({
    name: candidate.name,
    address: candidate.address,
    google_place_id: candidate.place_id,
  })
}

function openManualForm() {
  focused.value = false
  showManualForm.value = true
  googleCandidates.value = []
}

function submitManual() {
  const name = query.value.trim()
  const address = manualAddress.value.trim()
  if (!name || !address) {
    error.value = '劇場名と住所を入力してください'
    return
  }
  registerTheater({ name, address })
}

function clearSelection() {
  emit('update:modelValue', '')
  query.value = ''
  googleCandidates.value = []
  showManualForm.value = false
}

function closeDropdown() {
  setTimeout(() => { focused.value = false }, 180)
}
</script>

<template>
  <div class="theater-picker">
    <div class="theater-search-row" :class="{ active: focused }">
      <IconSearch :size="15" />
      <input
        v-model="query"
        type="text"
        autocomplete="off"
        placeholder="劇場名・エリアで検索"
        aria-label="劇場を検索"
        @input="handleInput"
        @focus="focused = true"
        @blur="closeDropdown"
      />
      <IconCheck v-if="modelValue" :size="16" class="selected-check" />
      <button v-if="query" type="button" class="clear-button" aria-label="劇場の選択を解除" @mousedown.prevent="clearSelection">
        <IconX :size="14" />
      </button>
    </div>

    <div v-if="focused && query.trim()" class="theater-results">
      <button
        v-for="theater in localMatches"
        :key="`local-${theater.id}`"
        type="button"
        class="theater-option"
        @mousedown.prevent="chooseExisting(theater)"
      >
        <strong>{{ theater.name }}</strong>
        <span v-if="theater.area_name || theater.address"><IconMapPin :size="11" />{{ theater.area_name || theater.address }}</span>
      </button>

      <div v-if="searchingGoogle" class="theater-searching">
        <IconLoader2 :size="14" class="spin" />Googleで劇場を確認中...
      </div>

      <template v-else-if="googleCandidates.length">
        <div class="option-divider"><span>Googleの候補</span></div>
        <button
          v-for="candidate in googleCandidates"
          :key="candidate.place_id"
          type="button"
          class="theater-option google-option"
          :disabled="registering"
          @mousedown.prevent="chooseGoogle(candidate)"
        >
          <strong>{{ candidate.name }}</strong>
          <span><IconMapPin :size="11" />{{ candidate.address }}</span>
        </button>
      </template>

      <button type="button" class="register-manually" @mousedown.prevent="openManualForm">
        <IconPlus :size="13" />見つからない場合は「{{ query.trim() }}」を登録
      </button>
    </div>

    <div v-if="showManualForm" class="manual-form">
      <div>
        <strong>{{ query.trim() }}</strong>
        <span>新しい劇場として登録</span>
      </div>
      <input v-model="manualAddress" type="text" placeholder="住所（市区町村まででも可）" aria-label="劇場の住所" />
      <div class="manual-actions">
        <button type="button" class="manual-cancel" @click="showManualForm = false">戻る</button>
        <button type="button" class="manual-submit" :disabled="registering" @click="submitManual">
          {{ registering ? '登録中...' : 'この劇場を登録' }}
        </button>
      </div>
    </div>

    <p v-if="error" class="theater-error">{{ error }}</p>
    <p v-if="selectedTheater && !selectedTheater.is_approved" class="pending-note">この劇場は確認中です。作品にはそのまま使用できます。</p>
  </div>
</template>

<style scoped>
.theater-picker { position: relative; }
.theater-search-row { display: flex; min-height: 39px; align-items: center; gap: .5rem; padding: 0 .65rem; border: 1px solid #52525b; border-radius: 8px; background: #212529; color: #71717a; }
.theater-search-row.active { border-color: #71717a; box-shadow: 0 0 0 3px rgba(244,63,94,.08); }
.theater-search-row input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; color: #fff; font-size: .8rem; }
.selected-check { color: #34d399; }
.clear-button { display: grid; width: 24px; height: 24px; padding: 0; place-items: center; border: 0; border-radius: 50%; background: rgba(255,255,255,.06); color: #a1a1aa; }
.theater-results { position: absolute; z-index: 30; top: calc(100% + 5px); left: 0; right: 0; max-height: 300px; overflow-y: auto; padding: .35rem; border: 1px solid rgba(255,255,255,.12); border-radius: 11px; background: #202023; box-shadow: 0 14px 34px rgba(0,0,0,.45); }
.theater-option { display: flex; width: 100%; flex-direction: column; gap: .22rem; padding: .62rem .65rem; border: 0; border-radius: 8px; background: transparent; color: #fff; text-align: left; }
.theater-option:hover { background: rgba(255,255,255,.06); }
.theater-option strong { font-size: .77rem; }
.theater-option span { display: flex; align-items: flex-start; gap: 3px; color: #71717a; font-size: .61rem; line-height: 1.45; }
.google-option { border-left: 2px solid rgba(66,133,244,.5); }
.option-divider { display: flex; align-items: center; gap: .5rem; margin: .3rem .4rem .15rem; color: #71717a; font: 500 .54rem Roboto, sans-serif; }
.option-divider::before, .option-divider::after { content: ''; height: 1px; flex: 1; background: rgba(255,255,255,.08); }
.theater-searching { display: flex; align-items: center; gap: .4rem; padding: .65rem; color: #71717a; font-size: .65rem; }
.spin { animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.register-manually { display: flex; width: 100%; align-items: center; gap: .35rem; padding: .65rem; border: 0; border-top: 1px solid rgba(255,255,255,.08); background: transparent; color: #fda4af; font-size: .68rem; text-align: left; }
.manual-form { display: flex; flex-direction: column; gap: .65rem; margin-top: .55rem; padding: .8rem; border: 1px solid rgba(244,63,94,.2); border-radius: 10px; background: rgba(244,63,94,.045); }
.manual-form > div:first-child { display: flex; flex-direction: column; gap: .15rem; }
.manual-form strong { color: #fff; font-size: .76rem; }
.manual-form span { color: #71717a; font-size: .62rem; }
.manual-form input { padding: .55rem .65rem; border: 1px solid #52525b; border-radius: 8px; outline: 0; background: #18181b; color: #fff; font-size: .75rem; }
.manual-actions { display: flex; justify-content: flex-end; gap: .5rem; }
.manual-actions button { padding: .42rem .7rem; border-radius: 8px; font-size: .66rem; font-weight: 700; }
.manual-cancel { border: 0; background: transparent; color: #a1a1aa; }
.manual-submit { border: 0; background: #fff; color: #18181b; }
.theater-error { margin: .45rem 0 0; color: #fb7185; font-size: .65rem; }
.pending-note { margin: .4rem 0 0; color: #a1a1aa; font-size: .61rem; }
</style>
