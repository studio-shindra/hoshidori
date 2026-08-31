<script setup>
import { computed, ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'
import {
  IconPencil, IconTrash, IconSparkles,
  IconChevronDown, IconChevronRight, IconBuildingStore, IconTheater, IconLogout, IconUserOff,
} from '@tabler/icons-vue'
import RatingButtons from '@/components/RatingButtons.vue'
import LogListItem from '@/components/LogListItem.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import AppLoader from '@/components/AppLoader.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const planned = ref([])
const watched = ref([])
const shops = ref([])
const activeTab = ref(['planned', 'watched'].includes(route.query.tab) ? route.query.tab : 'planned')
const archiveMeta = ref([])
const activeYear = ref(new Date().getFullYear())
const loading = ref(true)
const todayDate = new Date().toLocaleDateString('sv-SE')

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return [...new Set([currentYear, ...archiveMeta.value.map((item) => item.year)])]
    .sort((a, b) => b - a)
})
const plannedTotal = computed(() => archiveMeta.value.reduce((sum, item) => sum + item.planned, 0))
const watchedTotal = computed(() => archiveMeta.value.reduce((sum, item) => sum + item.watched, 0))
const activeLogs = computed(() => activeTab.value === 'planned' ? planned.value : watched.value)
const groupedLogs = computed(() => {
  const groups = new Map()
  for (const log of activeLogs.value) {
    const month = log.watched_on ? Number(log.watched_on.slice(5, 7)) : 0
    if (!groups.has(month)) groups.set(month, [])
    groups.get(month).push(log)
  }
  const direction = activeTab.value === 'planned' ? 1 : -1
  return [...groups.entries()]
    .sort((a, b) => (a[0] - b[0]) * direction)
    .map(([month, logs]) => ({
      month,
      label: month ? `${month}月` : '日付未設定',
      logs,
    }))
})

function yearCount(year) {
  const row = archiveMeta.value.find((item) => item.year === year)
  return row?.[activeTab.value] || 0
}

async function fetchArchive(year) {
  const [pData, wData] = await Promise.all([
    api.getFresh(`/api/viewing-logs/archive/?status=planned&year=${year}`),
    api.getFresh(`/api/viewing-logs/archive/?status=watched&year=${year}`),
  ])
  planned.value = pData.results || []
  watched.value = wData.results || []
}

async function selectYear(year) {
  if (activeYear.value === year) return
  activeYear.value = year
  loading.value = true
  try {
    await fetchArchive(year)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage' } })
    return
  }
  try {
    const [metaData, shopData] = await Promise.all([
      api.getFresh('/api/viewing-logs/archive-meta/'),
      api.get('/api/shops/'),
    ])
    archiveMeta.value = metaData.years || []
    const currentYear = new Date().getFullYear()
    activeYear.value = currentYear
    await fetchArchive(activeYear.value)
    shops.value = shopData.results || shopData
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
})

// 編集
const editingLog = ref(null)
const editMemo = ref('')
const editWatchedOn = ref('')
const editWatchedTime = ref('')
const editRating = ref('')
const editAfterShop = ref('')
const editLoading = ref(false)

function startEdit(log) {
  editingLog.value = log.id
  editMemo.value = log.memo || ''
  editWatchedOn.value = log.watched_on || ''
  editWatchedTime.value = log.watched_time || ''
  editRating.value = log.rating || ''
  editAfterShop.value = log.after_shop || ''
}

function cancelEdit() {
  editingLog.value = null
}

async function saveEdit(log) {
  editLoading.value = true
  try {
    const body = {
      performance: log.performance,
      status: log.status,
      memo: editMemo.value,
      watched_on: editWatchedOn.value || null,
      watched_time: editWatchedTime.value || null,
      after_shop: editAfterShop.value || null,
    }
    const updated = await api.patch(`/api/viewing-logs/${log.id}/`, body)
    Object.assign(log, updated)
    const metaData = await api.getFresh('/api/viewing-logs/archive-meta/')
    archiveMeta.value = metaData.years || []
    await fetchArchive(activeYear.value)
    editingLog.value = null
  } catch {
    /* empty */
  } finally {
    editLoading.value = false
  }
}

async function deleteLog(log, list) {
  if (!confirm('この記録を削除しますか？')) return
  try {
    await api.delete(`/api/viewing-logs/${log.id}/`)
    const idx = list.findIndex((l) => l.id === log.id)
    if (idx !== -1) list.splice(idx, 1)
    const meta = archiveMeta.value.find((item) => item.year === Number(log.watched_on?.slice(0, 4)))
    if (meta && meta[log.status] > 0) meta[log.status]--
  } catch {
    /* empty */
  }
}

async function logout() {
  await auth.logout()
  router.push('/')
}

</script>

<template>
  <div class="pt-4 pb-3">
    <!-- Header -->
    <div class="mb-4">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <UserAvatar :src="auth.user?.avatar_url" :name="auth.user?.display_name || auth.user?.username" :size="48" />
          <div class="d-flex flex-column lh-1 gap-1">
            <span class="fw-semibold">{{ auth.user?.display_name || auth.user?.username }}</span>
            <span class="small text-secondary">@{{ auth.user?.username }}</span>
          </div>
        </div>
        <RouterLink to="/mypage/edit" class="profile-edit-icon" aria-label="プロフィールを編集">
          <IconPencil :size="17" />
        </RouterLink>
      </div>
      <p v-if="auth.user?.bio" class="p-2 mt-3 border-top border-secondary">{{ auth.user.bio }}</p>

    </div>

    <AppLoader v-if="loading" />

    <template v-else>
      <!-- Tabs -->
      <div class="d-flex border-bottom border-secondary mb-3">
        <button
          class="shelf-tab flex-fill"
          :class="{ active: activeTab === 'planned' }"
          @click="activeTab = 'planned'"
        >
          <span>観る</span>
          <span class="tab-count">{{ plannedTotal }}</span>
        </button>
        <button
          class="shelf-tab flex-fill"
          :class="{ active: activeTab === 'watched' }"
          @click="activeTab = 'watched'"
        >
          <span>観た</span>
          <span class="tab-count">{{ watchedTotal }}</span>
        </button>
      </div>

      <div class="archive-controls mb-4">
        <label class="year-picker">
          <select :value="activeYear" aria-label="表示する年" @change="selectYear(Number($event.target.value))">
            <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
          </select>
          <IconChevronDown :size="14" />
        </label>
        <span class="year-total">{{ activeYear }}年 · {{ yearCount(activeYear) }}本</span>
      </div>

      <section class="archive-shelf">
        <div v-if="groupedLogs.length" class="d-flex flex-column gap-4">
          <section v-for="group in groupedLogs" :key="group.month" class="month-group">
            <div class="month-heading">
              <h2>{{ group.label }}</h2>
              <span>{{ group.logs.length }}本</span>
            </div>
            <div class="month-line"></div>

            <div class="d-flex flex-column gap-2 mt-2">
              <div v-for="log in group.logs" :key="log.id" class="card bg-dark border-0">
                <template v-if="editingLog === log.id">
                  <div class="d-flex flex-column gap-2">
                    <div class="fw-medium small">{{ log.work_title }}</div>
                    <div class="d-flex gap-2">
                      <input v-model="editWatchedOn" type="date" :max="activeTab === 'watched' ? todayDate : undefined" class="form-control bg-dark border-secondary text-light form-control-sm" />
                      <input v-model="editWatchedTime" type="time" class="form-control bg-dark border-secondary text-light form-control-sm" style="max-width: 7rem" />
                    </div>
                    <template v-if="activeTab === 'watched'">
                      <RatingButtons v-model="editRating" />
                      <div>
                        <label class="tiny text-secondary d-flex align-items-center gap-1 mb-1"><IconSparkles :size="12" />その後行った店</label>
                        <select v-model="editAfterShop" class="form-select bg-dark border-secondary text-light form-select-sm">
                          <option value="">選択しない</option>
                          <option v-for="shop in shops" :key="shop.id" :value="shop.id">{{ shop.name }}</option>
                        </select>
                      </div>
                      <textarea v-model="editMemo" rows="3" placeholder="メモ（任意）" class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
                    </template>
                    <div class="d-flex gap-2">
                      <button class="btn btn-primary-rose btn-sm flex-fill" :disabled="editLoading" @click="saveEdit(log)">{{ editLoading ? '保存中...' : '保存' }}</button>
                      <button class="btn btn-dark btn-sm flex-fill text-secondary" @click="cancelEdit">キャンセル</button>
                      <button class="btn btn-sm text-danger" aria-label="観劇記録を削除" @click="deleteLog(log, activeLogs)"><IconTrash :size="14" /></button>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <LogListItem
                    :work-title="log.work_title"
                    :work-slug="log.work_slug"
                    :watched-on="log.watched_on"
                    :watched-time="log.watched_time"
                    :theater-name="log.theater_name"
                    :memo="activeTab === 'watched' ? log.memo : ''"
                    :rating="activeTab === 'watched' ? log.rating : ''"
                    :images="activeTab === 'watched' ? log.images : []"
                    :after-shop-name="log.after_shop_name"
                  >
                    <template #action>
                      <button class="btn btn-link btn-sm p-0 text-secondary" aria-label="観劇記録を編集" @click.prevent.stop="startEdit(log)"><IconPencil :size="16" /></button>
                    </template>
                  </LogListItem>
                </template>
              </div>
            </div>
          </section>
        </div>
        <div v-else class="archive-empty text-center py-5">
          <IconSparkles :size="24" class="mb-2" />
          <p class="text-secondary mb-3">{{ activeYear }}年の{{ activeTab === 'planned' ? '観る予定' : '観劇記録' }}はまだありません</p>
          <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
        </div>
      </section>

      <section class="more-section mt-5 mb-4">
        <h2 class="tiny text-secondary fw-bold mb-2 px-1">その他</h2>
        <div class="more-list">
          <RouterLink :to="auth.isShopUser ? '/dashboard' : '/shops/for-business'" class="more-row">
            <span class="d-flex align-items-center gap-2"><IconBuildingStore :size="17" />{{ auth.isShopUser ? '店舗ダッシュボード（Web）' : '掲載店になりたい方はこちら' }}</span>
            <IconChevronRight :size="16" />
          </RouterLink>
          <RouterLink to="/theaters" class="more-row">
            <span class="d-flex align-items-center gap-2"><IconTheater :size="17" />劇場を探す</span>
            <IconChevronRight :size="16" />
          </RouterLink>
          <RouterLink to="/terms" class="more-row"><span>利用規約</span><IconChevronRight :size="16" /></RouterLink>
          <RouterLink to="/privacy" class="more-row"><span>プライバシーポリシー</span><IconChevronRight :size="16" /></RouterLink>
          <RouterLink to="/commerce" class="more-row"><span>特定商取引法に基づく表記</span><IconChevronRight :size="16" /></RouterLink>
          <RouterLink to="/guidelines" class="more-row"><span>投稿ガイドライン</span><IconChevronRight :size="16" /></RouterLink>
          <RouterLink to="/blocked-users" class="more-row">
            <span class="d-flex align-items-center gap-2"><IconUserOff :size="17" />ブロック中のユーザー</span>
            <IconChevronRight :size="16" />
          </RouterLink>
          <RouterLink to="/contact" class="more-row"><span>お問い合わせ</span><IconChevronRight :size="16" /></RouterLink>
          <button class="more-row more-logout" @click="logout">
            <span class="d-flex align-items-center gap-2"><IconLogout :size="17" />ログアウト</span>
          </button>
        </div>
        <p class="tiny text-secondary text-center mt-3 mb-0">© 2026 HOSHIDORI</p>
      </section>

    </template>
  </div>
</template>

<style scoped>
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.review-body {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.shelf-tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #a1a1aa;
  padding: 0.75rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  cursor: pointer;

  &.active {
    color: #fff;
    border-bottom-color: #fff;
  }
}
.tab-count { color: #71717a; font-size: .68rem; font-weight: 700; }
.shelf-tab.active .tab-count { color: #d4d4d8; }
.profile-edit-icon { width: 34px; height: 34px; display: grid; place-items: center; border: 1px solid rgba(255,255,255,.09); border-radius: 50%; color: #a1a1aa; background: rgba(255,255,255,.035); }
.profile-edit-icon:hover { color: #fff; }
.archive-controls { display: flex; align-items: center; justify-content: space-between; }
.year-picker { position: relative; display: inline-flex; align-items: center; color: #a1a1aa; }
.year-picker select { min-width: 92px; padding: .42rem 1.8rem .42rem .65rem; appearance: none; border: 1px solid rgba(255,255,255,.1); border-radius: 9px; outline: 0; background: #18181b; color: #e4e4e7; font-size: .75rem; font-weight: 700; }
.year-picker svg { position: absolute; right: .55rem; pointer-events: none; }
.year-total { color: #71717a; font-size: .64rem; }
.month-heading { display: flex; align-items: baseline; justify-content: space-between; padding: 0 .15rem; }
.month-heading h2 { margin: 0; color: #f4f4f5; font-size: 1.02rem; font-weight: 800; }
.month-heading span { color: #71717a; font-size: .64rem; }
.month-line { width: 30px; height: 2px; margin-top: .45rem; border-radius: 99px; background: #f43f5e; box-shadow: 0 0 8px rgba(244,63,94,.45); }
.archive-empty { border: 1px dashed rgba(255,255,255,.12); border-radius: 14px; color: #52525b; }
.more-list {
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: #18181b;
}
.more-row {
  width: 100%;
  min-height: 46px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: transparent;
  color: #d4d4d8;
  font-size: 0.78rem;
  text-decoration: none;
}
.more-row:last-child { border-bottom: 0; }
.more-row:hover { color: #fff; background: rgba(255, 255, 255, 0.025); }
.more-logout { color: #a1a1aa; }
</style>
