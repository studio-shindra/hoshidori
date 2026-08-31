<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/lib/api'
import {
  IconBuildingStore, IconCheck, IconClick, IconCreditCard, IconPhoto,
  IconSparkles, IconStarFilled,
} from '@tabler/icons-vue'

const route = useRoute()
const data = ref(null)
const loading = ref(true)
const saving = ref(false)
const imageUploading = ref(false)
const billingLoading = ref(false)
const error = ref('')
const notice = ref('')
const form = reactive({})

const status = computed(() => data.value?.shop?.application_status || '')
const statusLabel = computed(() => ({
  pending: '審査中', listed: '無料掲載中', recommended: 'おすすめ店',
})[status.value] || '')
const isSubscribed = computed(() => ['active', 'trialing'].includes(data.value?.subscription?.status))
const maxDaily = computed(() => Math.max(
  ...(data.value?.daily_after_viewing_counts || []).map((day) => day.count), 1,
))

function applyShop(shop) {
  for (const field of [
    'name', 'category', 'description', 'address', 'nearest_station', 'distance_note',
    'website_url', 'instagram_url', 'tabelog_url', 'google_map_url', 'phone_number',
    'opening_hours_text', 'benefit_text',
  ]) form[field] = shop[field] || ''
}

async function load() {
  loading.value = true
  try {
    data.value = await api.getFresh('/api/dashboard/')
    applyShop(data.value.shop)
  } catch (requestError) {
    error.value = requestError.status === 404 ? '店舗が登録されていません' : 'データを取得できませんでした'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (route.query.checkout === 'success') notice.value = 'お申し込みを受け付けました。反映まで少し時間がかかる場合があります。'
  if (route.query.checkout === 'cancelled') notice.value = 'お申し込みはキャンセルされました。'
  await load()
})

async function save() {
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    const shop = await api.patch('/api/dashboard/', form)
    data.value.shop = shop
    notice.value = '店舗情報を保存しました。'
  } catch {
    error.value = '店舗情報を保存できませんでした。'
  } finally {
    saving.value = false
  }
}

async function uploadImage(event) {
  const file = event.target.files?.[0]
  if (!file) return
  imageUploading.value = true
  error.value = ''
  const body = new FormData()
  body.append('image', file)
  try {
    data.value.shop = await api.upload('/api/dashboard/image/', body)
    notice.value = '店舗画像を保存しました。'
  } catch (requestError) {
    error.value = requestError.data?.image?.[0] || '画像を保存できませんでした。'
  } finally {
    imageUploading.value = false
    event.target.value = ''
  }
}

async function openCheckout() {
  billingLoading.value = true
  error.value = ''
  try {
    const result = await api.post('/api/dashboard/checkout/')
    window.location.href = result.url
  } catch (requestError) {
    error.value = requestError.status === 503
      ? '決済の準備中です。設定完了後にお申し込みいただけます。'
      : '決済画面を開けませんでした。'
    billingLoading.value = false
  }
}

async function openBillingPortal() {
  billingLoading.value = true
  error.value = ''
  try {
    const result = await api.post('/api/dashboard/billing-portal/')
    window.location.href = result.url
  } catch {
    error.value = 'お支払い管理画面を開けませんでした。'
    billingLoading.value = false
  }
}

function formatDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<template>
  <div class="dashboard-page pb-5">
    <header class="dashboard-header">
      <div>
        <span class="eyebrow">FOR SHOPS</span>
        <h1>店舗ダッシュボード</h1>
      </div>
      <RouterLink to="/" class="return-link">ホシドリへ戻る →</RouterLink>
    </header>

    <p v-if="loading" class="text-center text-secondary py-5">読み込み中...</p>
    <div v-else-if="error && !data" class="panel text-center text-danger">{{ error }}</div>
    <template v-else-if="data">
      <div v-if="notice" class="notice success"><IconCheck :size="17" />{{ notice }}</div>
      <div v-if="error" class="notice error">{{ error }}</div>

      <section class="status-panel" :class="status">
        <div class="status-icon">
          <IconStarFilled v-if="status === 'recommended'" :size="22" />
          <IconBuildingStore v-else :size="22" />
        </div>
        <div class="status-copy">
          <span>掲載ステータス</span>
          <h2>{{ statusLabel }}</h2>
          <p v-if="status === 'pending'">申請内容を確認しています。承認後にホシドリへ掲載されます。</p>
          <p v-else-if="status === 'listed'">通常掲載として公開中です。情報はいつでも更新できます。</p>
          <p v-else>ホシドリおすすめ店として優先表示されています。</p>
        </div>
        <RouterLink v-if="data.shop.is_active" :to="`/shops/${data.shop.slug}`" class="preview-link">掲載ページを見る</RouterLink>
      </section>

      <div class="dashboard-grid">
        <main class="dashboard-content">
          <section class="panel">
            <div class="panel-heading">
              <div><span>PROFILE</span><h2>店舗情報</h2></div>
              <label class="image-button">
                <IconPhoto :size="16" />{{ imageUploading ? '送信中' : '画像を変更' }}
                <input type="file" accept="image/jpeg,image/png,image/webp" :disabled="imageUploading" @change="uploadImage" />
              </label>
            </div>
            <form class="profile-form" @submit.prevent="save">
              <div class="field-row">
                <label><span>店舗名</span><input v-model="form.name" required /></label>
                <label><span>カテゴリー</span><input v-model="form.category" /></label>
              </div>
              <label><span>住所</span><input v-model="form.address" required /></label>
              <div class="field-row">
                <label><span>最寄り駅</span><input v-model="form.nearest_station" /></label>
                <label><span>劇場からの案内</span><input v-model="form.distance_note" /></label>
              </div>
              <label><span>店舗紹介</span><textarea v-model="form.description" rows="3" /></label>
              <div class="field-row">
                <label><span>電話番号</span><input v-model="form.phone_number" type="tel" /></label>
                <label><span>営業時間</span><input v-model="form.opening_hours_text" /></label>
              </div>
              <label><span>公式サイト</span><input v-model="form.website_url" type="url" /></label>
              <label><span>Instagram</span><input v-model="form.instagram_url" type="url" /></label>
              <label><span>Google Maps</span><input v-model="form.google_map_url" type="url" /></label>
              <label><span>観劇客への案内・特典</span><textarea v-model="form.benefit_text" rows="2" /></label>
              <button class="save-button" type="submit" :disabled="saving">{{ saving ? '保存中...' : '変更を保存' }}</button>
            </form>
          </section>

          <section class="panel">
            <div class="panel-heading"><div><span>REPORT</span><h2>送客レポート</h2></div></div>
            <div class="stats-grid">
              <div class="stat"><IconStarFilled :size="15" /><span>その後行った店</span><strong>{{ data.after_viewing_total }}</strong><small>累計</small></div>
              <div class="stat"><IconSparkles :size="15" /><span>今月の送客</span><strong>{{ data.after_viewing_this_month }}</strong><small>件</small></div>
              <div class="stat"><IconClick :size="15" /><span>ページ閲覧</span><strong>{{ data.click_total }}</strong><small>累計</small></div>
              <div class="stat"><IconClick :size="15" /><span>今日の閲覧</span><strong>{{ data.click_today }}</strong><small>件</small></div>
            </div>
            <div v-if="data.daily_after_viewing_counts?.length" class="daily-report">
              <h3>直近7日の送客</h3>
              <div v-for="day in data.daily_after_viewing_counts" :key="day.date" class="bar-row">
                <span>{{ formatDate(day.date) }}</span>
                <div><i :style="{ width: `${day.count / maxDaily * 100}%` }"></i></div>
                <b>{{ day.count }}</b>
              </div>
            </div>
            <div v-if="data.top_works?.length" class="works-report">
              <h3>観劇作品別</h3>
              <div v-for="work in data.top_works" :key="work.work_title"><span>{{ work.work_title }}</span><b>{{ work.count }}</b></div>
            </div>
            <p v-if="!data.after_viewing_total && !data.click_total" class="empty-report">掲載後のデータがここに表示されます。</p>
          </section>
        </main>

        <aside class="billing-column">
          <section class="plan-panel">
            <span class="plan-label">PLAN</span>
            <template v-if="isSubscribed">
              <div class="plan-star"><IconStarFilled :size="24" /></div>
              <h2>{{ data.subscription.plan_name }}</h2>
              <div class="plan-price">¥{{ data.subscription.monthly_price.toLocaleString() }}<small>/月（税込）</small></div>
              <p>おすすめ店として優先表示中です。</p>
              <button v-if="data.subscription.can_manage_billing" class="secondary-button" :disabled="billingLoading" @click="openBillingPortal"><IconCreditCard :size="16" />支払い情報を管理</button>
            </template>
            <template v-else>
              <div class="plan-star"><IconStarFilled :size="24" /></div>
              <h2>{{ data.recommended_plan.name }}</h2>
              <div class="plan-price">¥{{ data.recommended_plan.monthly_price.toLocaleString() }}<small>/月（税込）</small></div>
              <ul><li>店を探すで優先表示</li><li>劇場周辺で優先表示</li><li>おすすめ店マーク</li></ul>
              <p class="renewal-note">毎月自動更新・いつでも解約可能です。解約後は現在の利用期間末で終了し、日割り返金はありません。</p>
              <button class="upgrade-button" :disabled="status === 'pending' || billingLoading" @click="openCheckout">{{ status === 'pending' ? '承認後に申込できます' : billingLoading ? '準備中...' : 'おすすめ店にする' }}</button>
              <p class="terms-note">申し込みにより<RouterLink to="/terms">利用規約</RouterLink>に同意したものとみなされます。</p>
              <p v-if="!data.recommended_plan.stripe_ready" class="setup-note">現在は決済テスト前の表示です。</p>
            </template>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard-page { max-width: 1060px; margin: 0 auto; }
.dashboard-header { padding: 34px 0 26px; display: flex; align-items: end; justify-content: space-between; }
.eyebrow, .panel-heading span, .plan-label { color: #fb7185; font-size: .62rem; font-weight: 900; letter-spacing: .14em; }
.dashboard-header h1 { margin: 5px 0 0; font-size: clamp(1.6rem, 4vw, 2.5rem); font-weight: 900; }
.return-link { color: #71717a; font-size: .68rem; text-decoration: none; }
.notice { margin-bottom: 14px; padding: 12px 14px; display: flex; align-items: center; gap: 8px; border-radius: 10px; font-size: .72rem; }
.notice.success { color: #d1fae5; background: rgba(16,185,129,.12); }
.notice.error { color: #fecdd3; background: rgba(244,63,94,.12); }
.status-panel, .panel, .plan-panel { border: 1px solid rgba(255,255,255,.09); border-radius: 17px; background: #151517; }
.status-panel { min-height: 118px; padding: 22px 24px; display: flex; align-items: center; gap: 17px; margin-bottom: 22px; }
.status-panel.recommended { border-color: rgba(245,158,11,.3); background: linear-gradient(120deg, rgba(245,158,11,.1), #151517 55%); }
.status-icon { width: 46px; height: 46px; flex: 0 0 auto; display: grid; place-items: center; border-radius: 13px; color: #fb7185; background: rgba(244,63,94,.12); }
.recommended .status-icon { color: #fbbf24; background: rgba(245,158,11,.14); }
.status-copy { min-width: 0; flex: 1; }
.status-copy > span { color: #71717a; font-size: .62rem; }
.status-copy h2 { margin: 2px 0 3px; font-size: 1.15rem; font-weight: 900; }
.status-copy p { margin: 0; color: #a1a1aa; font-size: .68rem; line-height: 1.6; }
.preview-link { padding: 8px 11px; border: 1px solid rgba(255,255,255,.12); border-radius: 9px; color: #d4d4d8; font-size: .65rem; text-decoration: none; white-space: nowrap; }
.dashboard-grid { display: grid; grid-template-columns: minmax(0, 1fr) 290px; gap: 22px; align-items: start; }
.dashboard-content { display: flex; flex-direction: column; gap: 22px; }
.panel { padding: clamp(18px, 3vw, 28px); }
.panel-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; }
.panel-heading h2 { margin: 3px 0 0; font-size: 1.15rem; font-weight: 850; }
.image-button { position: relative; padding: 8px 11px; display: flex; align-items: center; gap: 6px; overflow: hidden; border: 1px solid rgba(255,255,255,.11); border-radius: 9px; color: #a1a1aa; font-size: .65rem; cursor: pointer; }
.image-button input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.profile-form { display: flex; flex-direction: column; gap: 15px; }
.profile-form label { display: flex; flex-direction: column; gap: 6px; color: #a1a1aa; font-size: .66rem; font-weight: 700; }
.profile-form input, .profile-form textarea { width: 100%; border: 1px solid rgba(255,255,255,.1); border-radius: 9px; outline: 0; background: #0d0d0f; color: #fff; font-size: .76rem; }
.profile-form input { height: 42px; padding: 0 12px; }
.profile-form textarea { padding: 10px 12px; resize: vertical; }
.profile-form input:focus, .profile-form textarea:focus { border-color: rgba(244,63,94,.65); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 13px; }
.save-button, .upgrade-button, .secondary-button { min-height: 44px; border: 0; border-radius: 10px; font-size: .72rem; font-weight: 850; }
.save-button { align-self: flex-end; min-width: 150px; padding: 0 18px; background: #f4f4f5; color: #111; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 9px; }
.stat { padding: 14px; display: grid; grid-template-columns: auto 1fr; gap: 4px 6px; border-radius: 11px; background: #0d0d0f; }
.stat svg { color: #fb7185; }
.stat span { color: #71717a; font-size: .58rem; }
.stat strong { grid-column: 1 / 2; font-size: 1.55rem; line-height: 1; }
.stat small { align-self: end; color: #52525b; font-size: .55rem; }
.daily-report, .works-report { margin-top: 24px; }
.daily-report h3, .works-report h3 { margin-bottom: 12px; color: #a1a1aa; font-size: .66rem; }
.bar-row { display: grid; grid-template-columns: 34px 1fr 20px; align-items: center; gap: 8px; margin-top: 7px; color: #71717a; font-size: .6rem; }
.bar-row > div { height: 9px; overflow: hidden; border-radius: 99px; background: #27272a; }
.bar-row i { height: 100%; display: block; border-radius: inherit; background: #f43f5e; }
.bar-row b { color: #d4d4d8; text-align: right; }
.works-report > div { padding: 8px 0; display: flex; justify-content: space-between; gap: 12px; border-top: 1px solid rgba(255,255,255,.07); font-size: .68rem; }
.works-report b { color: #fb7185; }
.empty-report { margin: 24px 0 0; color: #52525b; font-size: .68rem; text-align: center; }
.billing-column { position: sticky; top: 80px; }
.plan-panel { padding: 23px; }
.plan-star { width: 44px; height: 44px; margin-top: 19px; display: grid; place-items: center; border-radius: 13px; color: #fbbf24; background: rgba(245,158,11,.13); }
.plan-panel h2 { margin: 16px 0 2px; font-size: 1rem; }
.plan-price { font-size: 1.75rem; font-weight: 900; }
.plan-price small { color: #71717a; font-size: .62rem; }
.plan-panel p { color: #71717a; font-size: .65rem; line-height: 1.6; }
.plan-panel .renewal-note { color: #a1a1aa; }
.terms-note { margin: 8px 0 0; text-align: center; }
.terms-note a { color: #a1a1aa; }
.plan-panel ul { margin: 18px 0; padding-left: 17px; color: #a1a1aa; font-size: .68rem; line-height: 2; }
.upgrade-button, .secondary-button { width: 100%; padding: 0 12px; }
.upgrade-button { background: #f43f5e; color: #fff; }
.secondary-button { display: flex; align-items: center; justify-content: center; gap: 6px; background: #f4f4f5; color: #111; }
.upgrade-button:disabled, .secondary-button:disabled { opacity: .48; }
.setup-note { margin: 9px 0 0; text-align: center; }
@media (max-width: 850px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .billing-column { position: static; grid-row: 1; }
}
@media (max-width: 620px) {
  .dashboard-header { padding-top: 24px; }
  .status-panel { align-items: flex-start; flex-wrap: wrap; padding: 18px; }
  .status-copy { min-width: calc(100% - 63px); }
  .preview-link { margin-left: 63px; }
  .field-row { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .save-button { width: 100%; }
}
</style>
