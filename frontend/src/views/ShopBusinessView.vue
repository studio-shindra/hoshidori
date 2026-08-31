<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import {
  IconBuildingStore, IconCheck, IconMapPin, IconSearch, IconSparkles,
} from '@tabler/icons-vue'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(true)
const submitting = ref(false)
const searching = ref(false)
const error = ref('')
const placeQuery = ref('')
const candidates = ref([])
const theaterQuery = ref('')
const theaterCandidates = ref([])
const selectedTheaters = ref([])
const form = reactive({
  name: '', category: '', description: '', address: '', nearest_station: '',
  website_url: '', instagram_url: '', google_map_url: '', google_place_id: '',
  phone_number: '', opening_hours_text: '', benefit_text: '', theater_ids: [],
})

onMounted(async () => {
  try {
    const data = await api.getFresh('/api/shop-application/')
    if (data.has_application) router.replace('/dashboard')
  } catch {
    error.value = '申請状況を確認できませんでした。'
  } finally {
    loading.value = false
  }
})

async function searchPlaces() {
  if (placeQuery.value.trim().length < 2) return
  searching.value = true
  error.value = ''
  try {
    const data = await api.getFresh(`/api/shop-place-candidates/?q=${encodeURIComponent(placeQuery.value.trim())}`)
    candidates.value = data.results || []
    if (!candidates.value.length) error.value = 'Google Mapsで候補が見つかりませんでした。手入力でも申請できます。'
  } catch {
    error.value = '店舗候補を取得できませんでした。手入力で続けられます。'
  } finally {
    searching.value = false
  }
}

function selectCandidate(candidate) {
  form.name = candidate.name
  form.address = candidate.address
  form.category = candidate.category
  form.google_map_url = candidate.google_map_url
  form.google_place_id = candidate.place_id
  candidates.value = []
  placeQuery.value = candidate.name
}

async function searchTheaters() {
  if (theaterQuery.value.trim().length < 1) return
  try {
    const data = await api.getFresh(`/api/theaters/?q=${encodeURIComponent(theaterQuery.value.trim())}`)
    theaterCandidates.value = (data.results || data).filter(
      (theater) => !selectedTheaters.value.some((selected) => selected.id === theater.id),
    )
  } catch {
    theaterCandidates.value = []
  }
}

function selectTheater(theater) {
  selectedTheaters.value.push(theater)
  form.theater_ids = selectedTheaters.value.map((item) => item.id)
  theaterCandidates.value = []
  theaterQuery.value = ''
}

function removeTheater(theater) {
  selectedTheaters.value = selectedTheaters.value.filter((item) => item.id !== theater.id)
  form.theater_ids = selectedTheaters.value.map((item) => item.id)
}

function errorText(requestError) {
  const data = requestError.data
  if (!data) return '申請を送信できませんでした。'
  if (typeof data === 'string') return data
  return Object.values(data).flat().join(' ')
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    await api.post('/api/shop-application/', form)
    await auth.fetchMe()
    router.replace('/dashboard')
  } catch (requestError) {
    error.value = errorText(requestError)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="business-page pb-5">
    <div class="business-hero">
      <div class="eyebrow"><IconSparkles :size="14" /> FOR SHOPS</div>
      <h1>観劇後の一杯を、<br />あなたのお店へ。</h1>
      <p>ホシドリへの通常掲載は無料です。店舗情報を申請すると、運営確認後に店を探すページや劇場周辺に表示されます。</p>
      <div class="steps">
        <span><b>1</b>無料申請</span><span><b>2</b>運営確認</span><span><b>3</b>掲載開始</span>
      </div>
    </div>

    <p v-if="loading" class="text-center text-secondary py-5">読み込み中...</p>
    <div v-else class="business-grid">
      <aside class="plan-card">
        <div class="plan-icon"><IconBuildingStore :size="24" /></div>
        <h2>通常掲載</h2>
        <div class="price">無料</div>
        <ul>
          <li><IconCheck :size="15" />店舗ページの掲載</li>
          <li><IconCheck :size="15" />劇場周辺への表示</li>
          <li><IconCheck :size="15" />送客レポート</li>
          <li><IconCheck :size="15" />店舗情報の編集</li>
        </ul>
        <p>おすすめ店へのアップグレードは、掲載承認後にダッシュボードから選べます。</p>
      </aside>

      <form class="application-card" @submit.prevent="submit">
        <div class="form-heading">
          <div>
            <span>無料掲載</span>
            <h2>店舗情報を申請</h2>
          </div>
          <IconMapPin :size="22" />
        </div>

        <label class="field-label">Google Mapsから店舗を探す</label>
        <div class="place-search">
          <input v-model="placeQuery" type="search" placeholder="店舗名とエリアを入力" @keydown.enter.prevent="searchPlaces" />
          <button type="button" :disabled="searching" @click="searchPlaces"><IconSearch :size="17" />{{ searching ? '検索中' : '検索' }}</button>
        </div>
        <div v-if="candidates.length" class="candidate-list">
          <button v-for="candidate in candidates" :key="candidate.place_id" type="button" @click="selectCandidate(candidate)">
            <strong>{{ candidate.name }}</strong><small>{{ candidate.address }}</small>
          </button>
        </div>
        <p class="form-note">見つからない場合は、下の項目を直接入力してください。</p>

        <label class="field-label">近くの劇場（複数選択可）</label>
        <div class="place-search">
          <input v-model="theaterQuery" type="search" placeholder="劇場名を入力" @keydown.enter.prevent="searchTheaters" />
          <button type="button" @click="searchTheaters"><IconSearch :size="17" />検索</button>
        </div>
        <div v-if="theaterCandidates.length" class="candidate-list">
          <button v-for="theater in theaterCandidates" :key="theater.id" type="button" @click="selectTheater(theater)">
            <strong>{{ theater.name }}</strong><small>{{ theater.area_name || theater.address }}</small>
          </button>
        </div>
        <div v-if="selectedTheaters.length" class="selected-theaters">
          <button v-for="theater in selectedTheaters" :key="theater.id" type="button" @click="removeTheater(theater)">{{ theater.name }} ×</button>
        </div>
        <p class="form-note">選んだ劇場の周辺店として表示されます。未選択でも申請できます。</p>

        <div class="form-fields">
          <label><span>店舗名 *</span><input v-model="form.name" required /></label>
          <div class="field-row">
            <label><span>カテゴリー</span><input v-model="form.category" placeholder="居酒屋、カフェなど" /></label>
            <label><span>最寄り駅</span><input v-model="form.nearest_station" /></label>
          </div>
          <label><span>住所 *</span><input v-model="form.address" required /></label>
          <label><span>店舗紹介</span><textarea v-model="form.description" rows="3" /></label>
          <div class="field-row">
            <label><span>電話番号</span><input v-model="form.phone_number" type="tel" /></label>
            <label><span>営業時間</span><input v-model="form.opening_hours_text" /></label>
          </div>
          <label><span>公式サイト</span><input v-model="form.website_url" type="url" placeholder="https://" /></label>
          <label><span>Instagram</span><input v-model="form.instagram_url" type="url" placeholder="https://instagram.com/" /></label>
          <label><span>観劇客への案内・特典（任意）</span><textarea v-model="form.benefit_text" rows="2" placeholder="チケット提示で50円引き など" /></label>
        </div>

        <p v-if="error" class="application-error">{{ error }}</p>
        <button class="submit-button" type="submit" :disabled="submitting">
          {{ submitting ? '送信中...' : '無料掲載を申請する' }}
        </button>
        <p class="legal-note">申請内容は運営が確認します。掲載開始前に内容確認のためご連絡する場合があります。</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.business-page { max-width: 1040px; margin: 0 auto; }
.business-hero { padding: 46px 0 38px; }
.eyebrow { display: flex; align-items: center; gap: 6px; color: #fb7185; font-size: .68rem; font-weight: 800; letter-spacing: .14em; }
.business-hero h1 { margin: 14px 0 12px; font-size: clamp(2rem, 6vw, 4rem); font-weight: 900; line-height: 1.12; letter-spacing: -.035em; }
.business-hero > p { max-width: 620px; margin: 0; color: #a1a1aa; font-size: .9rem; line-height: 1.9; }
.steps { display: flex; flex-wrap: wrap; gap: 12px 24px; margin-top: 26px; color: #d4d4d8; font-size: .75rem; }
.steps span { display: flex; align-items: center; gap: 8px; }
.steps b { width: 22px; height: 22px; display: grid; place-items: center; border: 1px solid rgba(244,63,94,.4); border-radius: 50%; color: #fb7185; font-size: .65rem; }
.business-grid { display: grid; grid-template-columns: minmax(220px, 290px) minmax(0, 1fr); gap: 24px; align-items: start; }
.plan-card, .application-card { border: 1px solid rgba(255,255,255,.09); border-radius: 18px; background: #151517; }
.plan-card { position: sticky; top: 86px; padding: 24px; }
.plan-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; color: #fb7185; background: rgba(244,63,94,.12); }
.plan-card h2 { margin: 20px 0 2px; font-size: 1rem; }
.price { font-size: 2rem; font-weight: 900; }
.plan-card ul { display: flex; flex-direction: column; gap: 10px; margin: 22px 0; padding: 0; list-style: none; color: #d4d4d8; font-size: .75rem; }
.plan-card li { display: flex; align-items: center; gap: 8px; }
.plan-card li svg { color: #fb7185; }
.plan-card p { margin: 0; color: #71717a; font-size: .66rem; line-height: 1.7; }
.application-card { padding: clamp(20px, 4vw, 34px); }
.form-heading { display: flex; justify-content: space-between; align-items: center; margin-bottom: 26px; }
.form-heading span { color: #fb7185; font-size: .66rem; font-weight: 800; }
.form-heading h2 { margin: 3px 0 0; font-size: 1.35rem; font-weight: 800; }
.form-heading > svg { color: #52525b; }
.field-label, .form-fields label { display: flex; flex-direction: column; gap: 7px; color: #a1a1aa; font-size: .69rem; font-weight: 700; }
.place-search { display: flex; gap: 8px; margin-top: 8px; }
.place-search input, .form-fields input, .form-fields textarea { width: 100%; border: 1px solid rgba(255,255,255,.12); border-radius: 10px; outline: 0; background: #0d0d0f; color: #fff; font-size: .78rem; }
.place-search input, .form-fields input { min-height: 44px; padding: 0 13px; }
.form-fields textarea { padding: 11px 13px; resize: vertical; }
.place-search input:focus, .form-fields input:focus, .form-fields textarea:focus { border-color: rgba(244,63,94,.7); box-shadow: 0 0 0 3px rgba(244,63,94,.08); }
.place-search button { min-width: 94px; display: flex; align-items: center; justify-content: center; gap: 6px; border: 0; border-radius: 10px; background: #f4f4f5; color: #111; font-size: .72rem; font-weight: 800; }
.candidate-list { margin-top: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,.09); border-radius: 10px; }
.candidate-list button { width: 100%; padding: 10px 12px; display: flex; flex-direction: column; gap: 2px; border: 0; border-bottom: 1px solid rgba(255,255,255,.07); background: #202023; color: #fff; text-align: left; }
.candidate-list button:last-child { border-bottom: 0; }
.candidate-list small, .form-note { color: #71717a; font-size: .62rem; }
.form-note { margin: 8px 0 24px; }
.selected-theaters { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 9px; }
.selected-theaters button { padding: 6px 9px; border: 1px solid rgba(244,63,94,.28); border-radius: 99px; background: rgba(244,63,94,.08); color: #fda4af; font-size: .64rem; }
.form-fields { display: flex; flex-direction: column; gap: 17px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.application-error { margin: 18px 0 0; color: #fb7185; font-size: .72rem; }
.submit-button { width: 100%; min-height: 50px; margin-top: 24px; border: 0; border-radius: 12px; background: #f43f5e; color: #fff; font-size: .8rem; font-weight: 900; }
.submit-button:disabled { opacity: .55; }
.legal-note { margin: 10px 0 0; color: #52525b; font-size: .6rem; line-height: 1.6; text-align: center; }
@media (max-width: 760px) {
  .business-hero { padding: 28px 2px 26px; }
  .business-grid { grid-template-columns: 1fr; }
  .plan-card { position: static; }
  .field-row { grid-template-columns: 1fr; }
}
</style>
