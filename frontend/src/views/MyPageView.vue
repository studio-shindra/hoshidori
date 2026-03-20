<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { IconEye, IconCalendar, IconPhoto, IconPencil, IconTrash, IconTicket, IconStar, IconCheck } from '@tabler/icons-vue'
import RatingButtons from '@/components/RatingButtons.vue'
import LogListItem from '@/components/LogListItem.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import WorkCard from '@/components/WorkCard.vue'
import AppLoader from '@/components/AppLoader.vue'

const auth = useAuthStore()
const router = useRouter()

const planned = ref([])
const watched = ref([])
const myPosters = ref([])
const activeTab = ref('planned')
const loading = ref(true)

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { next: '/mypage' } })
    return
  }
  try {
    const [pData, wData, posterData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
      api.get('/api/works/my-posters/'),
    ])
    planned.value = pData.results || pData
    watched.value = wData.results || wData
    myPosters.value = Array.isArray(posterData) ? posterData : posterData.results || []
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
const editLoading = ref(false)

function startEdit(log) {
  editingLog.value = log.id
  editMemo.value = log.memo || ''
  editWatchedOn.value = log.watched_on || ''
  editWatchedTime.value = log.watched_time || ''
  editRating.value = log.rating || ''
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
    }
    const updated = await api.patch(`/api/viewing-logs/${log.id}/`, body)
    Object.assign(log, updated)
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
  } catch {
    /* empty */
  }
}

// ポスター選択・削除
const selectedPoster = ref(null)

function togglePosterSelect(id) {
  selectedPoster.value = selectedPoster.value === id ? null : id
}

async function deletePoster(id) {
  if (!confirm('このポスターを削除しますか？')) return
  try {
    await api.delete(`/api/works/my-posters/${id}/`)
    myPosters.value = myPosters.value.filter((p) => p.id !== id)
    selectedPoster.value = null
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
        <div class="d-flex justify-content-between align-items-start mb-2">
          <RouterLink to="/mypage/edit" class="btn btn-sm btn-light text-dark">編集</RouterLink>
        </div>
      </div>
      <p v-if="auth.user?.bio" class="p-2 mt-3 border-top border-secondary">{{ auth.user.bio }}</p>

    </div>

    <AppLoader v-if="loading" />

    <template v-else>
      <!-- Tabs -->
      <div class="d-flex border-bottom border-secondary mb-3">
        <button
          class="shelf-tab flex-fill gap-2"
          :class="{ active: activeTab === 'planned' }"
          @click="activeTab = 'planned'"
        >
          <div class="df-center gap-1">
            <IconTicket :size="18" />
            <span>観る</span>
          </div>
          <span class="fw-bold">{{ planned.length }}</span>
        </button>
        <button
          class="shelf-tab flex-fill gap-2"
          :class="{ active: activeTab === 'watched' }"
          @click="activeTab = 'watched'"
        >
          <div class="df-center gap-1">
            <IconStar :size="18" />
            <span>観た</span>
          </div>
          <span class="fw-bold">{{ watched.length }}</span>
        </button>
        <button
          class="shelf-tab flex-fill gap-2"
          :class="{ active: activeTab === 'posters' }"
          @click="activeTab = 'posters'"
        >
          <div class="df-center gap-1">
            <IconPhoto :size="18" />
            <span>ポスター</span>
          </div>
          <span class="fw-bold">{{ myPosters.length }}</span>
        </button>
      </div>

      <!-- Tab: これから観る -->
      <section v-if="activeTab === 'planned'">
        <div v-if="planned.length" class="d-flex flex-column gap-2">
          <div v-for="log in planned" :key="log.id" class="card bg-dark border-0">
            <!-- 編集モード -->
            <template v-if="editingLog === log.id">
              <div class="d-flex flex-column gap-2">
                <div class="fw-medium small">{{ log.work_title }}</div>
                <div class="d-flex gap-2">
                  <button class="btn btn-primary-rose btn-sm flex-fill" :disabled="editLoading" @click="saveEdit(log)">{{ editLoading ? '保存中...' : '保存' }}</button>
                  <button class="btn btn-dark btn-sm flex-fill text-secondary" @click="cancelEdit">キャンセル</button>
                  <button class="btn btn-sm text-danger" @click="deleteLog(log, planned)"><IconTrash :size="14" /></button>
                </div>
              </div>
            </template>
            <!-- 通常表示 -->
            <template v-else>
              <LogListItem
                :poster-url="log.poster_url"
                :work-title="log.work_title"
                :work-slug="log.work_slug"
                :theater-name="log.theater_name"
              >
                <template #action>
                  <div class="position-absolute top-0 end-0 p-2">
                    <button class="btn btn-link btn-sm p-0 text-secondary" @click="startEdit(log)"><IconPencil :size="16" /></button>
                  </div>
                </template>
              </LogListItem>
            </template>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">観る作品はまだありません</p>
          <div class="d-flex flex-column gap-2 align-items-center">
            <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
            <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
          </div>
        </div>
      </section>

      <!-- Tab: 観た -->
      <section v-if="activeTab === 'watched'">
        <div v-if="watched.length" class="d-flex flex-column gap-2">
          <div v-for="log in watched" :key="log.id" class="card bg-dark border-0">
            <!-- 編集モード -->
            <template v-if="editingLog === log.id">
              <div class="d-flex flex-column gap-2">
                <div class="fw-medium small">{{ log.work_title }}</div>
                <div class="d-flex gap-2">
                  <input v-model="editWatchedOn" type="date" class="form-control bg-dark border-secondary text-light form-control-sm" />
                  <input v-model="editWatchedTime" type="time" class="form-control bg-dark border-secondary text-light form-control-sm" style="max-width: 7rem" />
                </div>
                <RatingButtons v-model="editRating" />
                <textarea v-model="editMemo" rows="3" placeholder="メモ（任意）" class="form-control bg-dark border-secondary text-light form-control-sm"></textarea>
                <div class="d-flex gap-2">
                  <button class="btn btn-primary-rose btn-sm flex-fill" :disabled="editLoading" @click="saveEdit(log)">{{ editLoading ? '保存中...' : '保存' }}</button>
                  <button class="btn btn-dark btn-sm flex-fill text-secondary" @click="cancelEdit">キャンセル</button>
                  <button class="btn btn-sm text-danger" @click="deleteLog(log, watched)"><IconTrash :size="14" /></button>
                </div>
              </div>
            </template>
            <!-- 通常表示 -->
            <template v-else>
              <LogListItem
                :poster-url="log.poster_url"
                :work-title="log.work_title"
                :work-slug="log.work_slug"
                :watched-on="log.watched_on"
                :watched-time="log.watched_time"
                :theater-name="log.theater_name"
                :memo="log.memo"
                :rating="log.rating"
                :images="log.images"
              >
                <template #action>
                  <div class="position-absolute top-0 end-0 p-2">
                    <button class="btn btn-link btn-sm p-0 text-secondary" @click="startEdit(log)"><IconPencil :size="16" /></button>
                  </div>
                </template>
              </LogListItem>
            </template>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">観た作品はまだありません</p>
          <div class="d-flex flex-column gap-2 align-items-center">
            <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探す</RouterLink>
            <RouterLink to="/logs/new" class="btn btn-sm btn-outline-secondary">記録する</RouterLink>
          </div>
        </div>
      </section>

      <!-- Tab: ポスター -->
      <section v-if="activeTab === 'posters'">
        <div v-if="myPosters.length" class="grid-wrapper">
          <div
            v-for="p in myPosters"
            :key="p.id"
            class="position-relative poster-selectable"
            :class="{ 'poster-selected': selectedPoster === p.id }"
            @click="togglePosterSelect(p.id)"
          >
            <WorkCard
              :poster-url="p.image_url || p.image"
              :work-title="p.work_title"
            />
            <div class="poster-check" :class="{ active: selectedPoster === p.id }">
              <IconCheck :size="14" />
            </div>
          </div>
        </div>
        <div v-if="selectedPoster" class="mt-3">
          <button class="btn btn-sm btn-outline-danger w-100" @click="deletePoster(selectedPoster)">
            <IconTrash :size="14" class="me-1" />選択中のポスターを削除
          </button>
        </div>
        <div v-else class="text-center py-5">
          <p class="text-secondary mb-3">まだポスター投稿はありません</p>
          <RouterLink to="/works" class="btn btn-sm btn-outline-secondary">作品を探して投稿する</RouterLink>
        </div>
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
  gap: 0.15rem;
  cursor: pointer;

  &.active {
    color: #fff;
    border-bottom-color: #fff;
  }
}
.poster-selectable {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 0.5rem;

  &.poster-selected {
    border-color: #f43f5e;
  }
}
.poster-check {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #a1a1aa;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  z-index: 1;

  &.active {
    background: #f43f5e;
    border-color: #f43f5e;
    color: #fff;
  }
}
</style>
