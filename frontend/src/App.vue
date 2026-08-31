<script setup>
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  IconHome,
  IconCoffee,
  IconSearch,
  IconPlus,
  IconUser,
} from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const transitionName = ref('page-forward')
let historyPosition = window.history.state?.position ?? 0
let isPopNavigation = false

function onPopState(event) {
  const nextPosition = event.state?.position ?? historyPosition
  transitionName.value = nextPosition < historyPosition ? 'page-back' : 'page-forward'
  isPopNavigation = true
}

const removeBeforeGuard = router.beforeEach(() => {
  if (!isPopNavigation) transitionName.value = 'page-forward'
})
const removeAfterGuard = router.afterEach(() => {
  historyPosition = window.history.state?.position ?? historyPosition
  window.setTimeout(() => { isPopNavigation = false }, 0)
})

onMounted(() => {
  auth.fetchMe()
  window.addEventListener('popstate', onPopState)
})
onBeforeUnmount(() => {
  window.removeEventListener('popstate', onPopState)
  removeBeforeGuard()
  removeAfterGuard()
})

const isAuthRoute = computed(() => ['login', 'register'].includes(route.name))
const isStandaloneRoute = computed(() => isAuthRoute.value || route.meta.merchantPage)

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

</script>

<template>
  <div class="app-shell" data-bs-theme="dark">
    <!-- Header -->
    <header class="position-fixed top-0 start-0 end-0 w-100 d-flex align-items-end">
      <div class="container d-flex align-items-center justify-content-center px-3 w-100 mx-auto">
        <RouterLink to="/" class="d-flex align-items-center text-decoration-none">
          <img src="/icon.svg" alt="HOSHIDORI" width="40" height="40" />
        </RouterLink>
      </div>
    </header>

    <main class="container pt-3 pb-5" :class="{ 'main-no-footer': isStandaloneRoute, 'merchant-main': route.meta.merchantPage }" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
      <div v-if="pullDistance > 0" class="pull-indicator" :style="{ height: pullDistance + 'px' }">
        <div class="pull-spinner" :class="{ active: pullDistance > 50 }" />
      </div>
      <RouterView v-slot="{ Component, route: resolvedRoute }">
        <Transition :name="transitionName" mode="out-in">
          <component :is="Component" :key="`${resolvedRoute.fullPath}:${viewKey}`" />
        </Transition>
      </RouterView>
    </main>

    <footer
      v-if="!isStandaloneRoute"
      style="z-index: 99999;"
      class="position-fixed bottom-0 start-0 end-0 bg-cdark">
      <nav class="container d-flex align-items-center justify-content-around pt-3" style="padding-bottom: calc(0.5rem + env(safe-area-inset-bottom))">
        <RouterLink to="/" class="nav-item" aria-label="ホーム" :class="{ active: route.path === '/' }">
          <IconHome :size="25" :stroke="1.55" />
        </RouterLink>
        <RouterLink to="/shops" class="nav-item" aria-label="店を探す" :class="{ active: route.path.startsWith('/shops') }">
          <IconCoffee :size="25" :stroke="1.55" />
        </RouterLink>
        <RouterLink to="/logs/new" class="nav-create" aria-label="記録する">
          <IconPlus :size="25" :stroke="1.7" />
        </RouterLink>
        <RouterLink to="/works" class="nav-item" aria-label="作品・出演者・劇場を探す" :class="{ active: route.path.startsWith('/works') || route.path.startsWith('/theaters') }">
          <IconSearch :size="25" :stroke="1.55" />
        </RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/mypage" class="nav-item" aria-label="マイページ" :class="{ active: route.path === '/mypage' }">
          <UserAvatar
            :src="auth.user?.avatar_url"
            :name="auth.user?.display_name || auth.user?.username"
            :size="32"
          />
        </RouterLink>
        <RouterLink v-else to="/login" class="nav-item" aria-label="ログイン" :class="{ active: route.path === '/login' }">
          <IconUser :size="26" />
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

header{
  height: calc(var(--header-height) + env(safe-area-inset-top));
  padding-top: env(safe-area-inset-top);
  z-index: 1020;
  background: transparent;
}

main{
  margin-top: calc(var(--header-height) + env(safe-area-inset-top));
  margin-bottom: calc(var(--header-height) + env(safe-area-inset-bottom));
}
.page-forward-enter-active,
.page-forward-leave-active,
.page-back-enter-active,
.page-back-leave-active { transition: transform .2s cubic-bezier(.22,.75,.26,1), opacity .18s ease; }
.page-forward-enter-from { transform: translateX(18px); opacity: 0; }
.page-forward-leave-to { transform: translateX(-10px); opacity: 0; }
.page-back-enter-from { transform: translateX(-18px); opacity: 0; }
.page-back-leave-to { transform: translateX(10px); opacity: 0; }
@media (prefers-reduced-motion: reduce) {
  .page-forward-enter-active,
  .page-forward-leave-active,
  .page-back-enter-active,
  .page-back-leave-active { transition: opacity .01s linear; }
}
.main-no-footer { margin-bottom: 0; }
.merchant-main { max-width: 1120px; }

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
    transition: color .16s ease, transform .12s ease;

    &:active { transform: scale(.9); }

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
    transition: transform .12s ease, filter .16s ease;
    &:active { transform: scale(.9); filter: brightness(.9); }
  }
}
</style>
