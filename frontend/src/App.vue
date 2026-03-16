<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted, ref } from 'vue'
import {
  IconHome,
  IconTheater,
  IconMasksTheater,
  IconPencil,
  IconUser,
  IconMenu2,
  IconX,
} from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const route = useRoute()
onMounted(() => auth.fetchMe())

const showSidebar = ref(false)

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
        <span class="fw-bold text-white small">HOSHIDORI</span>
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
      <div class="mt-auto px-3 pb-4">
        <button class="btn btn-dark btn-sm w-100 text-white mb-2 fw-bold" @click="logout">ログアウト</button>
        <p class="text-secondary mb-0" style="font-size: 0.65rem;">&copy; 2026 HOSHIDORI</p>
      </div>
    </aside>

    <!-- Header -->
    <header class="position-absolute top-0 start-0 end-0 w-100 d-flex align-items-center">
      <div class="container d-flex align-items-center justify-content-between px-3 w-100 mx-auto position-relative">
        <div class="position-absolute top-50 start-50 translate-middle">
          <RouterLink to="/" class="d-flex align-items-center text-decoration-none">
            <img src="/icon.svg" alt="HOSHIDORI" width="40" height="40" />
          </RouterLink>
        </div>
        <button class="btn-icon" @click="showSidebar = true">
          <IconMenu2 :size="22" />
        </button>
        <div>
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/mypage" class="user-link">
              <UserAvatar :src="auth.user.avatar_url" :name="auth.user.display_name || auth.user.username" :size="28" />
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/login" class="login-link">ログイン</RouterLink>
          </template>
        </div>
      </div>
    </header>

    <main class="container pt-3 pb-5">
      <RouterView />
    </main>

    <footer
    style="z-index: 99999;"
      class="position-fixed bottom-0 start-0 end-0 border-top border-secondary bg-cdark">
      <nav class="container d-flex align-items-center justify-content-around py-3">
        <RouterLink to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <IconHome :size="22" />
          <span>ホーム</span>
        </RouterLink>
        <RouterLink to="/theaters" class="nav-item" :class="{ active: route.path.startsWith('/theaters') }">
          <IconTheater :size="22" />
          <span>劇場</span>
        </RouterLink>
        <RouterLink to="/works" class="nav-item" :class="{ active: route.path.startsWith('/works') }">
          <IconMasksTheater :size="22" />
          <span>作品</span>
        </RouterLink>
        <RouterLink to="/logs/new" class="nav-item" :class="{ active: route.path.startsWith('/logs') }">
          <IconPencil :size="22" />
          <span>記録</span>
        </RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/mypage" class="nav-item" :class="{ active: route.path === '/mypage' }">
          <IconUser :size="22" />
          <span>観劇棚</span>
        </RouterLink>
        <RouterLink v-else to="/login" class="nav-item" :class="{ active: route.path === '/login' }">
          <IconUser :size="22" />
          <span>ログイン</span>
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
  height: 56px;
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
  height: var(--header-height);
  z-index: 1020;
}

main{
  margin-top: var(--header-height);
  margin-bottom: var(--header-height);
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
}
</style>
