<!-- src/pages/LogNewPage.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { request, fetchWorks as apiFetchWorks } from '@/apiClient'
import { onLogSaveSuccess } from '@/lib/admobHelpers'
import Multiselect from '@vueform/multiselect'
import { IconClick, IconBinoculars, IconArmchair, IconStar, IconPencil } from '@tabler/icons-vue'
import SimpleSpinner from '@/components/LoadingSimpleSpinner.vue'

const router = useRouter()

const works = ref([])
const runs = ref([])
const todayTimes = ref([])
const loading = ref(true)
const error = ref(null)

const form = ref({
  workId: '',
  runId: '',
  watchedDate: '',
  watchedTime: '',
  seat: '',
  memo: '',
  rating: '',
})

// 日時選択用
const selectedDate = ref('')
const selectedHour = ref('13')
const selectedMinute = ref('00')

// スライダー用の一時的な値（JavaScript で管理、v-model は使わない）
const sliderValue = ref('')
const sliderInputRef = ref(null)

// 時間の選択肢（0-23時）
const hourOptions = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))

function setMinute(minute) {
  selectedMinute.value = minute
}

function onSliderInput(e) {
  // スライダーの値を表示用に更新（v-model ではなく手動更新）
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
  loading.value = true
  try {
    const data = await apiFetchWorks()
    works.value = data
    // 初期選択はしない
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchRunsAndTimes(workId) {
  try {
    // Runs取得
    const workDetail = await request(`/api/works/${workId}/`)
    runs.value = workDetail.runs || []
    // 今日の公演時間候補取得
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
    // 作品が未選択の場合はRunsをクリア
    runs.value = []
    todayTimes.value = []
  }
}

// 簡易登録
async function handleQuickCreate() {
  if (!quickForm.value.title) {
    alert('タイトルは必須です')
    return
  }
  
  try {
    const newWork = await request('/api/works/create_or_get/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: quickForm.value.title,
        troupe_name: quickForm.value.troupe || null,
        theater_name: quickForm.value.theater || null,
        status: 'DRAFT'
      })
    })
    
    // 作品リストに追加して選択
    works.value.push(newWork)
    form.value.workId = newWork.id
    await fetchRunsAndTimes(newWork.id)
    
    // フォームをリセット
    showQuickForm.value = false
    quickForm.value = { title: '', troupe: '', theater: '' }
  } catch (e) {
    alert('作品の登録に失敗しました: ' + e.message)
  }
}

// マルチセレクト用のオプション
const workOptions = computed(() => 
  works.value.map(w => ({
    value: w.id,
    label: `${w.title}（${w.main_theater?.name || w.theater?.name || ''}）`
  }))
)

// 時間候補ボタンをクリックした時
function setTimeCandidate(time) {
  // 今日の日付と候補時間を結合
  const today = new Date().toISOString().split('T')[0]
  form.value.watchedDate = `${today}T${time}`
}

onMounted(() => {
  fetchWorks()
  // 初期値: 今日の日付と13:00
  const today = new Date().toISOString().split('T')[0]
  selectedDate.value = today
  selectedHour.value = '13'
  selectedMinute.value = '00'
})

async function handleSubmit(e) {
  e.preventDefault()

  // スライダーの値をフォームに反映（送信時のみ）
  form.value.rating = sliderValue.value

  // watched_atを日付+時間で構築
  let watchedAt = null
  if (selectedDate.value) {
    watchedAt = `${selectedDate.value}T${selectedHour.value}:${selectedMinute.value}:00`
  }

  try {
    const payload = {
      work: Number(form.value.workId),
      run: form.value.runId ? Number(form.value.runId) : null,
      watched_at: watchedAt,
      memo: form.value.memo || null,
      rating: form.value.rating ? Number(form.value.rating) : null,
      tags: [],
    }

    // seat が空文字列の場合は送らない（null も送らない）
    if (form.value.seat) {
      payload.seat = form.value.seat
    }

    await request('/api/logs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    // 保存成功：インタースティシャル広告を表示（3回に1回）
    await onLogSaveSuccess()

    router.push('/logs')
  } catch (error) {
    console.error('ログの保存に失敗しました:', error)
    alert('ログの保存に失敗しました。もう一度お試しください。')
  }
}

</script>

<template>
  <main class="container py-4">
    <h1 class="mb-3 fw-bold text-center fs-3">観劇ログを追加</h1>

    <SimpleSpinner :show="loading" />
    
    <p v-if="error">エラー: {{ error }}</p>

    <form v-if="!loading && !error" @submit="handleSubmit" class="mb-4">
      <div class="wrap">
        <label class="form-label"><IconClick/>作品を選択</label>
        <Multiselect
          v-model="form.workId"
          :options="workOptions"
          :searchable="true"
          :close-on-select="true"
          placeholder="検索 & 選択"
          :no-options-text="'見つかりません'"
          @select="onWorkChange"
        />
        
        <!-- 見つからない場合の2つのオプション -->
        <div class="p-3">

          <!-- 簡易登録フォーム -->
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
            <!-- <button
              type="button"
              class="btn btn-sm btn-success w-100"
              @click="handleQuickCreate"
            >
              登録
            </button> -->
          </div>
          <div class="wrap df-center">
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

      <!-- <div class="mb-3" v-if="form.workId && runs.length > 0">
        <label class="form-label">公演ブロック</label>
        <select class="form-select" v-model="form.runId">
          <option value="">選択なし</option>
          <option
            v-for="run in runs"
            :key="run.id"
            :value="run.id"
          >
            {{ run.label }}（{{ run.area }}）
          </option>
        </select>
      </div> -->

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

        <!-- 日付選択 -->
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

        <!-- 時刻選択 -->
        <div class="mb-3 row df-center g-1">
          <div class="col-3">
            <label class="form-label small">時刻</label>
          </div>
          <div class="col-9">
            <div class="d-flex align-items-center gap-2">
              <select class="form-select" v-model="selectedHour" style="width: 80px;">
                <option v-for="hour in hourOptions" :key="hour" :value="hour">
                  {{ hour }}時
                </option>
              </select>
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

      <!-- スライダーセクション -->
      <div class="row mb-3 df-center g-1 mt-4 border-bottom pb-2">
        <div class="col-2 df-center">
          <div class="wrap df-center flex-column">
            <IconStar :size="12"/>
            <span class="fs-4">
              {{ sliderValue ? Number(sliderValue).toFixed(1) : '-' }}
            </span>
          </div>
        </div>
        <div class="col-10">
          <input
            ref="sliderInputRef"
            type="range"
            min="1"
            max="5"
            step="0.1"
            class="form-range mb-0"
            @input="onSliderInput"
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

      <button type="submit" class="btn btn-primary w-100">
        保存
      </button>
    </form>
  </main>
</template><style src="@vueform/multiselect/themes/default.css"></style>
