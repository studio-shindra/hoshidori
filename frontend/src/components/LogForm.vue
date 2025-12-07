<!-- src/components/LogForm.vue -->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { request, fetchWorks as apiFetchWorks } from '@/apiClient'
import Multiselect from '@vueform/multiselect'
import { IconClick, IconBinoculars, IconArmchair, IconStar, IconClock, IconTag } from '@tabler/icons-vue'
import SimpleSpinner from '@/components/LoadingSimpleSpinner.vue'

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => ['create', 'edit'].includes(value)
  },
  initialValue: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'delete'])

const router = useRouter()

const works = ref([])
const runs = ref([])
const todayTimes = ref([])
const dataLoading = ref(true)
const error = ref(null)
const tags = ref([])

const form = ref({
  workId: '',
  runId: '',
  watchedDate: '',
  watchedTime: '',
  seat: '',
  memo: '',
  rating: '',
  selectedTags: [],
})

// 日時選択用
const selectedDate = ref('')
const selectedHour = ref('13')
const selectedMinute = ref('00')

// スライダー用の一時的な値
const sliderValue = ref('')
const sliderInputRef = ref(null)

// 時間の選択肢（0-23時）
const hourOptions = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))

function setMinute(minute) {
  selectedMinute.value = minute
}

function onSliderInput(e) {
  sliderValue.value = e.target.value
}

// 簡易登録用フォーム
const showQuickForm = ref(false)
const quickForm = ref({
  title: '',
  troupe: '',
  theater: ''
})

async function fetchWorks() {
  dataLoading.value = true
  try {
    const data = await apiFetchWorks()
    works.value = data
  } catch (e) {
    error.value = e.message
  } finally {
    dataLoading.value = false
  }
}

async function fetchTags() {
  try {
    const data = await request('/api/tags/')
    tags.value = data
  } catch (e) {
    console.error('Failed to fetch tags:', e)
  }
}

async function fetchRunsAndTimes(workId) {
  try {
    const workDetail = await request(`/api/works/${workId}/`)
    runs.value = workDetail.runs || []
    const timesData = await request(`/api/works/${workId}/today_times/`)
    todayTimes.value = timesData.times || []
  } catch (e) {
    console.error('Failed to fetch runs/times:', e)
  }
}

async function onWorkChange() {
  if (form.value.workId) {
    await fetchRunsAndTimes(form.value.workId)
    form.value.runId = ''
    form.value.watchedTime = ''
  } else {
    runs.value = []
    todayTimes.value = []
  }
}

// 簡易登録
async function handleQuickCreate() {
  const title = quickForm.value.title.trim()

  if (!title) {
    alert('タイトルは必須です')
    return null
  }

  try {
    const newWork = await request('/api/works/create_or_get/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        troupe_name: quickForm.value.troupe || null,
        theater_name: quickForm.value.theater || null,
        status: 'DRAFT'
      })
    })

    // 一覧に追加して選択状態にする
    works.value.push(newWork)
    form.value.workId = newWork.id
    await fetchRunsAndTimes(newWork.id)

    // かんたんフォームをリセット＆閉じる
    showQuickForm.value = false
    quickForm.value = { title: '', troupe: '', theater: '' }

    return newWork
  } catch (e) {
    alert('作品の登録に失敗しました: ' + (e.message || '不明なエラー'))
    return null
  }
}

const workOptions = computed(() => 
  works.value.map(w => ({
    value: w.id,
    label: `${w.title}（${w.main_theater?.name || w.theater?.name || ''}）`
  }))
)

function setTimeCandidate(time) {
  const today = new Date().toISOString().split('T')[0]
  selectedDate.value = today
  const [hour, minute] = time.split(':')
  selectedHour.value = hour
  selectedMinute.value = minute
}

// 初期値の設定
function initializeForm() {
  if (props.initialValue) {
    // 編集モード：既存データで初期化
    form.value.workId = props.initialValue.work?.id || ''
    form.value.runId = props.initialValue.run || ''
    form.value.seat = props.initialValue.seat || ''
    form.value.memo = props.initialValue.memo || ''
    form.value.rating = props.initialValue.rating || ''
    form.value.selectedTags = props.initialValue.tags || []
    
    // 日時の設定
    if (props.initialValue.watchedDate) {
      const dateStr = props.initialValue.watchedDate
      selectedDate.value = dateStr.split('T')[0]
      const timeStr = dateStr.split('T')[1]
      if (timeStr) {
        const [hour, minute] = timeStr.split(':')
        selectedHour.value = hour
        selectedMinute.value = minute || '00'
      }
    }
    
    // rating をスライダーに反映
    if (props.initialValue.rating) {
      sliderValue.value = props.initialValue.rating
    }
    
    // 作品が選択されている場合、runs を取得
    if (form.value.workId) {
      fetchRunsAndTimes(form.value.workId)
    }
  } else {
    // 新規モード：デフォルト値
    const today = new Date().toISOString().split('T')[0]
    selectedDate.value = today
    selectedHour.value = '13'
    selectedMinute.value = '00'
  }
}

onMounted(() => {
  fetchWorks()
  fetchTags()
  initializeForm()
})

watch(() => props.initialValue, () => {
  initializeForm()
}, { deep: true })

async function handleSubmit(e) {
  e.preventDefault()

  // 1) 作品IDが無いときの特別処理（かんたん登録と共存させる）
  if (!form.value.workId) {
    const hasQuickTitle = quickForm.value.title && quickForm.value.title.trim().length > 0

    if (showQuickForm.value && hasQuickTitle) {
      // かんたん登録タイトルが入っていれば、先に作品を自動作成
      const created = await handleQuickCreate()
      if (!created) {
        // 作成に失敗したらログ保存に進まない
        return
      }
    } else {
      alert('作品を選択するか、かんたん登録でタイトルを入力してください')
      return
    }
  }

  // 2) ここまで来たら workId は必ずある前提
  form.value.rating = sliderValue.value

  let watchedAt = null
  if (selectedDate.value) {
    watchedAt = `${selectedDate.value}T${selectedHour.value}:${selectedMinute.value}:00`
  }

  const payload = {
    work_id: Number(form.value.workId),
    run: form.value.runId ? Number(form.value.runId) : null,
    watched_at: watchedAt,
    watchedDate: watchedAt,
    memo: form.value.memo || null,
    rating: form.value.rating ? Number(form.value.rating) : null,
    tags: form.value.selectedTags || [],
  }

  if (form.value.seat) {
    payload.seat = form.value.seat
  }

  // 画面で選択している作品情報をそのままローカル保存に渡す
  const selectedWork = works.value.find((w) => w.id === Number(form.value.workId)) || null
  if (selectedWork) {
    payload.work = selectedWork
  }

  emit('submit', payload)
}

function handleDelete() {
  emit('delete')
}
</script>

<template>
  <SimpleSpinner :show="dataLoading" />
  
  <p v-if="error">エラー: {{ error }}</p>

  <form v-if="!dataLoading && !error" @submit="handleSubmit" class="mb-4">
    <div class="wrap">
      <label class="form-label"><IconClick/>作品を選択</label>
      <Multiselect
        v-model="form.workId"
        :options="workOptions"
        :searchable="true"
        :close-on-select="true"
        placeholder="検索 & 選択"
        :no-options-text="'見つかりません'"
        @change="onWorkChange"
      />
      
      <div class="p-3">
        <div v-if="showQuickForm" class="mb-3 p-3 rounded bg-light">
          <div class="mb-1 text-center fw-bold">かんたん登録</div>
          <div class="mb-2">
            <label class="form-label small">タイトル *</label>
            <input
              type="text"
              class="form-control"
              v-model="quickForm.title"
              placeholder="作品名"
            />
          </div>
          <div class="mb-2">
            <label class="form-label small">団体名</label>
            <input
              type="text"
              class="form-control"
              v-model="quickForm.troupe"
              placeholder="団体名"
            />
          </div>
          <div class="mb-2">
            <label class="form-label small">劇場</label>
            <input
              type="text"
              class="form-control"
              v-model="quickForm.theater"
              placeholder="劇場名"
            />
          </div>
        </div>
        <div class="wrap df-center ">
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary mb-1"
            @click="showQuickForm = !showQuickForm"
          >
            {{ showQuickForm ? '閉じる' : '作品が見つからない場合' }}
          </button>
        </div>
        <div class="df-center">
          <button
            type="button"
            class="btn btn-sm btn-link"
            @click="router.push('/works/new')"
          >
            作品登録ページ
          </button>
        </div>
      </div>
    </div>

    <div class="mb-3">
      <div v-if="todayTimes.length > 0" class="d-flex align-items-center gap-4 my-4">
        <small class="badge bg-danger text-white">今日の公演候補</small>
        <div class="wrap d-flex gap-2">
          <button
            v-for="time in todayTimes"
            :key="time"
            type="button"
            class="btn btn-sm btn-outline-secondary"
            @click="setTimeCandidate(time)"
          >
            {{ time }}
          </button>
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconBinoculars/>観劇日</label>
        </div>
        <div class="col-9">
          <input
            type="date"
            class="form-control"
            v-model="selectedDate"
          />
        </div>
      </div>

      <div class="mb-3 row df-center g-1">
        <div class="col-3">
          <label class="form-label small"><IconClock />時刻</label>
        </div>
        <div class="col-9">
          <div class="d-flex align-items-center gap-2">
            <div class="row row-cols-2 w-100 g-2">
              <div class="col">
                <select class="form-select w-100" v-model="selectedHour">
                  <option v-for="hour in hourOptions" :key="hour" :value="hour">
                    {{ hour }}時
                  </option>
                </select>
              </div>
              <div class="col df-center gap-2">
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="selectedMinute === '00' ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="setMinute('00')"
                >
                  00分
                </button>
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="selectedMinute === '30' ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="setMinute('30')"
                >
                  30分
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-3 row df-center g-1">
      <div class="col-3">
        <label class="form-label small"><IconArmchair />座席</label>
      </div>
      <div class="col-9">
        <input
          type="text"
          class="form-control"
          v-model="form.seat"
          placeholder="A列12番 など"
        />
      </div>
    </div>

    <div class="mb-3 row df-center g-1 border-bottom pb-4">
      <div class="col-3">
        <label class="form-label small"><IconTag />タグ</label>
      </div>
      <div class="col-9">
        <Multiselect
          v-model="form.selectedTags"
          :options="tags"
          mode="tags"
          :searchable="true"
          :create-option="true"
          placeholder="選択 or 入力..."
          :no-options-text="'見つかりません'"
        />
      </div>
    </div>

    <div class="row mb-3 df-center g-1 mt-3 pb-2">
      <div class="col-3 d-flex align-items-center justify-content-start ps-4">
        <div class="wrap df-center flex-column">
          <IconStar :size="12"/>
          <span class="fs-4">
            {{ sliderValue ? Number(sliderValue).toFixed(1) : '-' }}
          </span>
        </div>
      </div>
      <div
       class="col-9"
       style="padding-right: 40px !important;">
        <input
          ref="sliderInputRef"
          type="range"
          min="1"
          max="5"
          step="0.1"
          class="form-range mb-0"
          @input="onSliderInput"
          :value="sliderValue"
        />
      </div>
    </div>

    <div class="mb-3">
      <textarea
        class="form-control"
        rows="3"
        v-model="form.memo"
        placeholder="あなたの観劇体験がより良いものでありますよう。感想をお書きください。"
        style="min-height: 200px;"
      />
    </div>

    <div v-if="mode === 'create'">
      <button type="submit" class="btn btn-primary w-100" :disabled="loading">
        保存
      </button>
    </div>

    <div v-else-if="mode === 'edit'" class="d-flex gap-2">
      <button type="submit" class="btn btn-primary flex-grow-1" :disabled="loading">
        保存
      </button>
      <button 
        type="button" 
        class="btn btn-danger"
        @click="handleDelete"
        :disabled="loading"
      >
        投稿を削除
      </button>
    </div>
  </form>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
