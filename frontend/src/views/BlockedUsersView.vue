<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { IconArrowLeft, IconUserOff } from '@tabler/icons-vue'
import { api } from '@/lib/api'
import AppLoader from '@/components/AppLoader.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const blocks = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const data = await api.getFresh('/api/user-blocks/')
    blocks.value = data.results || data
  } catch {
    error.value = 'ブロック中のユーザーを読み込めませんでした。'
  } finally {
    loading.value = false
  }
})

async function unblock(block) {
  try {
    await api.delete(`/api/user-blocks/${block.id}/`)
    blocks.value = blocks.value.filter((item) => item.id !== block.id)
  } catch {
    error.value = 'ブロックを解除できませんでした。'
  }
}
</script>

<template>
  <div class="blocked-page pt-4 pb-5">
    <RouterLink to="/mypage" class="back-link"><IconArrowLeft :size="16" />マイページ</RouterLink>
    <h1 class="fs-4 fw-bold mt-4 mb-1">ブロック中のユーザー</h1>
    <p class="small text-secondary mb-4">ブロックしたユーザーの投稿は表示されません。</p>

    <AppLoader v-if="loading" />
    <p v-else-if="error" class="small text-danger">{{ error }}</p>
    <div v-else-if="blocks.length" class="blocked-list">
      <div v-for="block in blocks" :key="block.id" class="blocked-row">
        <div class="d-flex align-items-center gap-2">
          <UserAvatar :src="block.blocked_avatar_url" :name="block.blocked_display_name" :size="36" />
          <span class="small fw-semibold">{{ block.blocked_display_name }}</span>
        </div>
        <button class="btn btn-sm btn-outline-secondary" @click="unblock(block)">解除</button>
      </div>
    </div>
    <div v-else class="blocked-empty text-center">
      <IconUserOff :size="24" class="mb-2" />
      <p class="small text-secondary mb-0">ブロック中のユーザーはいません</p>
    </div>
  </div>
</template>

<style scoped>
.back-link { display: inline-flex; align-items: center; gap: 4px; color: #a1a1aa; font-size: .72rem; text-decoration: none; }
.blocked-list { overflow: hidden; border: 1px solid rgba(255,255,255,.09); border-radius: 13px; background: #18181b; }
.blocked-row { display: flex; align-items: center; justify-content: space-between; padding: .85rem; border-bottom: 1px solid rgba(255,255,255,.08); }
.blocked-row:last-child { border-bottom: 0; }
.blocked-empty { padding: 3rem 1rem; border: 1px dashed rgba(255,255,255,.13); border-radius: 13px; color: #52525b; }
</style>
