<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import { IconMask, IconMessageCircle, IconTicket, IconStar } from '@tabler/icons-vue'
import WorkCard from '@/components/WorkCard.vue'
import LogListItem from '@/components/LogListItem.vue'

const auth = useAuthStore()
const loading = ref(true)
const plannedLogs = ref([])
const watchedLogs = ref([])

const plannedCount = computed(() => plannedLogs.value.length)
const watchedCount = computed(() => watchedLogs.value.length)

async function fetchData() {
  loading.value = true
  try {
    const [pData, wData] = await Promise.all([
      api.get('/api/viewing-logs/?status=planned'),
      api.get('/api/viewing-logs/?status=watched'),
    ])
    plannedLogs.value = pData.results || pData
    watchedLogs.value = wData.results || wData
  } catch {
    /* empty */
  } finally {
    loading.value = false
  }
}

watch(
  () => auth.isAuthenticated,
  (val) => {
    if (val) {
      fetchData()
    } else {
      loading.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <div>


    <!-- Not logged in -->
    <template v-if="!auth.isAuthenticated">
      <div class="px-3 py-5 text-center">
        <IconMask :size="48" class="text-secondary mb-3" />
        <p class="text-secondary mb-3">あなたの観劇体験を記録しよう</p>
        <div class="d-flex gap-2 justify-content-center">
          <RouterLink to="/login" class="btn btn-primary-rose px-4">ログイン</RouterLink>
          <RouterLink to="/register" class="btn btn-dark px-4">新規登録</RouterLink>
        </div>
        <div class="mt-4">
          <RouterLink to="/works" class="text-secondary small">作品を探す →</RouterLink>
        </div>
      </div>
    </template>

    <!-- Logged in -->
    <template v-else>
      <p v-if="loading" class="text-center text-secondary py-4">読み込み中...</p>
      <template v-else>

        <!-- これから観る -->
        <section v-if="plannedLogs.length" class="mb-4">
          <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
            <IconTicket :size="20" />
            Clip
            <span class="count-circle">{{ plannedCount }}</span>
          </h2>
          <div class="d-flex gap-2 overflow-auto scroll-hide">
            <WorkCard
              v-for="log in plannedLogs"
              :key="log.id"
              :poster-url="log.poster_url"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :theater-name="log.theater_name"
            />
          </div>
        </section>

        <!-- 最近観た作品 -->
        <section v-if="watchedLogs.length" class="mb-4">
          <h2 class="d-flex align-items-center gap-2 fw-bold mb-3 fs-2">
            <IconStar :size="20" />
            Watched
            <span class="count-circle">{{ watchedCount }}</span></h2>
          <div class="d-flex flex-column gap-3">
            <LogListItem
              v-for="log in watchedLogs"
              :key="log.id"
              :poster-url="log.poster_url"
              :work-title="log.work_title"
              :work-slug="log.work_slug"
              :watched-on="log.watched_on"
              :watched-time="log.watched_time"
              :theater-name="log.theater_name"
              :theater-area="log.theater_area"
              :memo="log.memo"
              :rating="log.rating"
            />
          </div>
        </section>

        <!-- 空の場合 -->
        <div v-if="!plannedLogs.length && !watchedLogs.length" class="px-3 py-4 text-center">
          <IconMessageCircle :size="36" class="text-secondary mb-2" />
          <p class="text-secondary small">まだ記録がありません</p>
          <RouterLink to="/works" class="btn btn-primary-rose btn-sm px-3">作品を探す</RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.count-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #fff;
  color: #000;
  font-size: 0.85rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
