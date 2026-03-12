<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'
import {
  IconHome,
  IconBuildingCommunity,
  IconMask,
  IconPencil,
  IconUser,
} from '@tabler/icons-vue'

const auth = useAuthStore()
const route = useRoute()
onMounted(() => auth.fetchMe())
</script>

<template>
  <div class="app-shell" data-bs-theme="dark">
    <header class="top-bar">
      <RouterLink to="/" class="brand">HOSHIDORI</RouterLink>
      <div class="top-right">
        <template v-if="auth.isAuthenticated">
          <RouterLink to="/mypage" class="user-link">
            <IconUser :size="18" />
            <span>{{ auth.user.display_name || auth.user.username }}</span>
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/login" class="login-link">ログイン</RouterLink>
        </template>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>

    <footer class="site-footer">
      <div class="footer-links">
        <RouterLink to="/terms">利用規約</RouterLink>
        <RouterLink to="/privacy">プライバシーポリシー</RouterLink>
        <RouterLink to="/guidelines">投稿ガイドライン</RouterLink>
        <RouterLink to="/contact">お問い合わせ</RouterLink>
      </div>
      <p class="footer-copy">&copy; 2026 HOSHIDORI</p>
    </footer>

    <nav class="bottom-nav">
      <RouterLink to="/" class="nav-item" :class="{ active: route.path === '/' }">
        <IconHome :size="22" />
        <span>ホーム</span>
      </RouterLink>
      <RouterLink to="/theaters" class="nav-item" :class="{ active: route.path.startsWith('/theaters') }">
        <IconBuildingCommunity :size="22" />
        <span>劇場</span>
      </RouterLink>
      <RouterLink to="/works" class="nav-item" :class="{ active: route.path.startsWith('/works') }">
        <IconMask :size="22" />
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
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #27272a;
  background: rgba(10, 10, 11, 0.95);
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
}
.brand {
  font-weight: 700;
  font-size: 1.1rem;
  color: #e4e4e7;
  text-decoration: none;
  letter-spacing: 0.05em;
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
.main-content {
  flex: 1;
  padding: 0;
  padding-bottom: 5rem;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
}
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 768px;
  display: flex;
  justify-content: space-around;
  background: rgba(10, 10, 11, 0.95);
  border-top: 1px solid #27272a;
  padding: 0.5rem 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 0.65rem;
  color: #71717a;
  text-decoration: none;
  padding: 0.25rem 0.5rem;
}
.nav-item.active {
  color: #f43f5e;
}
.site-footer {
  text-align: center;
  padding: 2rem 1rem 6rem;
  border-top: 1px solid #27272a;
  margin-top: 2rem;
}
.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem 1rem;
  margin-bottom: 0.75rem;
}
.footer-links a {
  font-size: 0.75rem;
  color: #71717a;
  text-decoration: none;
}
.footer-links a:hover {
  color: #a1a1aa;
}
.footer-copy {
  font-size: 0.65rem;
  color: #52525b;
  margin: 0;
}
</style>
