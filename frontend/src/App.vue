<script setup>
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted, ref } from 'vue'
import {
  IconHome,
  IconCoffee,
  IconMasksTheater,
  IconPlus,
  IconUser,
  IconMenu2,
  IconX,
} from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
onMounted(() => auth.fetchMe())

const showSidebar = ref(false)

// Pull to Refresh
const pullStart = ref(0)
const pullDistance = ref(0)
const refreshing = ref(false)
const viewKey = ref(0)

function onTouchStart(e) {
  if (window.scrollY === 0) {
    pullStart.value = e.touches[0].clientY
  } else {
    pullStart.value = 0
  }
}
function onTouchMove(e) {
  if (!pullStart.value) return
  const dist = e.touches[0].clientY - pullStart.value
  pullDistance.value = Math.max(0, Math.min(dist * 0.5, 80))
}
async function onTouchEnd() {
  if (pullDistance.value > 50 && !refreshing.value) {
    refreshing.value = true
    viewKey.value++
    refreshing.value = false
  }
  pullDistance.value = 0
  pullStart.value = 0
}

async function logout() {
  await auth.logout()
  showSidebar.value = false
  window.location.href = '/'
}
</script>

<template>
  <div class="app-shell" data-bs-theme="dark">

    <!-- Backdrop -->
    <Transition name="fade">
      <div v-if="showSidebar" class="sidebar-backdrop" @click="showSidebar = false" />
    </Transition>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-open': showSidebar }">
      <div class="sidebar-header d-flex align-items-center justify-content-between px-3 border-bottom border-secondary">
        <span></span>
        <button class="btn-icon" @click="showSidebar = false">
          <IconX :size="20" />
        </button>
      </div>
      <nav class="d-flex flex-column gap-1 p-3">
        <RouterLink to="/terms" class="sidebar-link" @click="showSidebar = false">利用規約</RouterLink>
        <RouterLink to="/privacy" class="sidebar-link" @click="showSidebar = false">プライバシーポリシー</RouterLink>
        <RouterLink to="/guidelines" class="sidebar-link" @click="showSidebar = false">投稿ガイドライン</RouterLink>
        <RouterLink to="/contact" class="sidebar-link" @click="showSidebar = false">お問い合わせ</RouterLink>
      </nav>
      <div class="mt-auto px-3" style="padding-bottom: calc(4rem + env(safe-area-inset-bottom));">
        <button class="btn btn-dark btn-sm w-100 text-white mb-2 fw-bold" @click="logout">ログアウト</button>
        <p class="text-secondary mb-0" style="font-size: 0.65rem;">&copy; 2026 HOSHIDORI</p>
      </div>
    </aside>

    <!-- Header -->
    <header class="position-fixed top-0 start-0 end-0 w-100 d-flex align-items-end bg-cdark">
      <div class="container d-flex align-items-center justify-content-between px-3 w-100 mx-auto position-relative">
        <div class="position-absolute top-50 start-50 translate-middle">
          <RouterLink to="/" class="d-flex align-items-center text-decoration-none">
            <img src="/icon.svg" alt="HOSHIDORI" width="40" height="40" />
          </RouterLink>
        </div>
        <button class="btn-icon" @click="showSidebar = true">
          <IconMenu2 :size="22" />
        </button>
      </div>
    </header>

    <main class="container pt-3 pb-5" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
      <div v-if="pullDistance > 0" class="pull-indicator" :style="{ height: pullDistance + 'px' }">
        <div class="pull-spinner" :class="{ active: pullDistance > 50 }" />
      </div>
      <RouterView :key="viewKey" />
    </main>

    <footer
    style="z-index: 99999;"
      class="position-fixed bottom-0 start-0 end-0 bg-cdark">
      <nav class="container d-flex align-items-center justify-content-around pt-3" style="padding-bottom: calc(0.5rem + env(safe-area-inset-bottom))">
        <RouterLink to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <IconHome :size="26" />
        </RouterLink>
        <RouterLink to="/shops" class="nav-item" :class="{ active: route.path.startsWith('/shops') }">
          <IconCoffee :size="26" />
        </RouterLink>
        <RouterLink to="/logs/new" class="nav-create">
          <IconPlus :size="26" />
        </RouterLink>
        <RouterLink to="/works" class="nav-item" :class="{ active: route.path.startsWith('/works') }">
          <IconMasksTheater :size="26" />
        </RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/mypage" class="nav-item" :class="{ active: route.path === '/mypage' }">
          <UserAvatar
            :src="auth.user?.avatar_url"
            :name="auth.user?.display_name || auth.user?.username"
            :size="32"
          />
        </RouterLink>
        <RouterLink v-else to="/login" class="nav-item" :class="{ active: route.path === '/login' }">
          <IconUser :size="26" />
          <span class="fw-bold">ログイン</span>
        </RouterLink>
      </nav>
    </footer>

  </div>
</template>

<style scoped>
.app-shell {
  --header-height: 56px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Sidebar */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1040;
}
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100dvh;
  background: #111;
  z-index: 1050;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.25s ease;
}
.sidebar-open {
  transform: translateX(0);
}
.sidebar-header {
  min-height: calc(56px + env(safe-area-inset-top));
  padding-top: env(safe-area-inset-top);
  flex-shrink: 0;
}
.sidebar-link {
  display: block;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: #a1a1aa;
  text-decoration: none;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;

  &:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
  }
}

/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Header */
.btn-icon {
  background: none;
  border: none;
  padding: 0.25rem;
  color: #a1a1aa;
  cursor: pointer;
  display: flex;
  align-items: center;

  &:hover {
    color: #fff;
  }
}
.user-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: #a1a1aa;
  text-decoration: none;
}
.login-link {
  font-size: 0.85rem;
  color: #a1a1aa;
}

header{
  height: calc(var(--header-height) + env(safe-area-inset-top));
  padding-top: env(safe-area-inset-top);
  z-index: 1020;
}

main{
  margin-top: calc(var(--header-height) + env(safe-area-inset-top));
  margin-bottom: calc(var(--header-height) + env(safe-area-inset-bottom));
}

/* Pull to Refresh */
.pull-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.pull-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #a1a1aa;
  border-radius: 50%;
  transition: border-top-color 0.2s;
  &.active {
    border-top-color: #f43f5e;
    animation: spin 0.7s linear infinite;
  }
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Bottom nav */
footer {
  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 0.65rem;
    color: white;
    text-decoration: none;
    padding: 0.25rem 0.5rem;

    &.active {
      color: #f43f5e;
    }
  }
  .nav-create {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: #f43f5e;
    color: #fff;
    text-decoration: none;
    flex-shrink: 0;
    margin-top: -8px;
  }
}
</style>
