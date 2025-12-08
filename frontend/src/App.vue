<script setup>
import { IconCategory, IconUser, IconLogin, IconLogout } from '@tabler/icons-vue'
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { AdMob, BannerAdSize, BannerAdPosition } from '@capacitor-community/admob'
import { Capacitor } from '@capacitor/core'
import PullToRefresh from 'pulltorefreshjs'
import { currentUser, getProfileInitial } from '@/authState'
import { isGuestUser } from '@/lib/localLogs'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()

// プラットフォーム検出
const isIOS = Capacitor.getPlatform() === 'ios'

// メニュー表示フラグ（開いているかどうか）
const showMenu = ref(false)
const appLoading = ref(true)

const isGuest = computed(() => isGuestUser() || !currentUser.value)
const userDisplayName = computed(() => {
  if (currentUser.value && currentUser.value.user) {
    return currentUser.value.user.username || 'User'
  }
  return null
})
const profileImageUrl = computed(() => currentUser.value?.profile_image)
const profileInitial = computed(() => getProfileInitial())

function logout() {
  localStorage.removeItem('hoshidori_token')
  localStorage.removeItem('hoshidori_refresh')
  currentUser.value = null
  closeMenu()
  location.href = '/'
}

// スワイプで操作する要素参照
const shell = ref(null)
const sideMenu = ref(null)
const overlay = ref(null)

// 右エッジドラッグ用の状態
const menuProgress = ref(0)         // 0 = 閉 / 1 = 全開
const isDraggingRight = ref(false)  // ドラッグ中かどうか

// エッジスワイプ用ハンドラ参照
let touchStartHandler = null
let touchMoveHandler = null
let touchEndHandler = null

// メニューのスタイルを一元管理
const sideMenuStyle = computed(() => {
  // menuProgress が 0 → 100% ずれてる（画面外）
  // menuProgress が 1 → 0%（全開）
  const translatePercent = 100 - menuProgress.value * 100

  return {
    transform: `translateX(${translatePercent}%)`,
    boxShadow: menuProgress.value > 0
      ? '-4px 0 20px rgba(0,0,0,0.15)'
      : 'none',
    transition: isDraggingRight.value
      ? 'none'
      : 'transform 0.2s ease-out',
  }
})

// 環境に応じてテスト/本番を自動切り替え（development: テスト / production: 本番）
const USE_TEST_ADS = import.meta.env.DEV

const ADMOB_IDS = {
  test: import.meta.env.VITE_ADMOB_BANNER_TEST_ID || 'ca-app-pub-3940256099942544/9214589741',
  production: import.meta.env.VITE_ADMOB_BANNER_PROD_ID || 'ca-app-pub-3940256099942544/1033173712'
}

function openMenu() {
  showMenu.value = true
  isDraggingRight.value = false
  menuProgress.value = 1
  const overlayEl = overlay.value
  if (overlayEl) {
    overlayEl.style.opacity = '0.6'
    overlayEl.style.pointerEvents = 'auto'
  }
}

function closeMenu() {
  showMenu.value = false
  isDraggingRight.value = false
  menuProgress.value = 0
  const overlayEl = overlay.value
  if (overlayEl) {
    overlayEl.style.opacity = '0'
    overlayEl.style.pointerEvents = 'none'
  }
}

onMounted(async () => {
  // AdMob
  try {
    await AdMob.initialize()
    await AdMob.showBanner({
      adId: USE_TEST_ADS ? ADMOB_IDS.test : ADMOB_IDS.production,
      adSize: BannerAdSize.BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
      margin: 64,
    })
  } catch (error) {
    console.error('AdMob initialization error:', error)
  }

  // Pull to Refresh 初期化
  PullToRefresh.init({
    mainElement: 'body',
    instructionsPullToRefresh: '',
    instructionsReleaseToRefresh: '',
    instructionsRefreshing: '',
    iconArrow: '',
    iconRefreshing: '',
    onRefresh() {
      window.location.reload()
    },
  })

  // 最低1.5秒はローディング表示
  setTimeout(() => {
    appLoading.value = false
  }, 1500)

  const shellEl = shell.value
  const overlayEl = overlay.value
  const menuEl = sideMenu.value
  if (!shellEl || !overlayEl || !menuEl) return

  let startX = 0
  let startY = 0
  let dragging = false
  let edge = 'none'
  let menuWidth = menuEl.offsetWidth || 280

  const EDGE = 20
  const MAX_SHIFT = 40
  const TRIGGER = 80

  const resetPositionLeft = () => {
    shellEl.style.transition = 'transform 0.15s ease-out'
    shellEl.style.transform = 'translateX(0px)'
    overlayEl.style.transition = 'opacity 0.15s ease-out'
    overlayEl.style.opacity = showMenu.value ? '0.6' : '0'
  }

  touchStartHandler = (e) => {
    if (e.touches.length !== 1) return
    const t = e.touches[0]
    startX = t.clientX
    startY = t.clientY
    dragging = false
    edge = 'none'

    const w = window.innerWidth || document.documentElement.clientWidth

    if (startX <= EDGE) {
      // 左エッジ → 戻るジェスチャ
      edge = 'left'
    } else if (startX >= w - EDGE) {
      // 右エッジ → サイドメニュー
      edge = 'right'
      menuWidth = menuEl.offsetWidth || 280
      isDraggingRight.value = true
      menuProgress.value = 0
      overlayEl.style.opacity = '0'
      overlayEl.style.pointerEvents = 'none'
    }
  }

  touchMoveHandler = (e) => {
    if (edge === 'none') return
    if (e.touches.length !== 1) return

    const t = e.touches[0]
    const dx = t.clientX - startX
    const dy = t.clientY - startY

    if (!dragging && Math.abs(dy) > Math.abs(dx)) return
    dragging = true

    // 左エッジ：戻るのヒントモーション
    if (edge === 'left') {
      e.preventDefault()
      if (dx <= 0) {
        shellEl.style.transform = 'translateX(0px)'
        overlayEl.style.opacity = showMenu.value ? '0.6' : '0'
        return
      }
      const shift = Math.min(dx, MAX_SHIFT)
      shellEl.style.transition = 'none'
      shellEl.style.transform = `translateX(${shift}px)`

      const ratio = shift / MAX_SHIFT
      overlayEl.style.transition = 'none'
      overlayEl.style.opacity = showMenu.value ? '0.6' : String(0.15 * ratio)
    }

    // 右エッジ：メニューを指に追従させる
    if (edge === 'right') {
      e.preventDefault()
      const pull = startX - t.clientX // 右→左方向に引っ張る量
      let progress = pull / menuWidth
      if (progress < 0) progress = 0
      if (progress > 1) progress = 1

      menuProgress.value = progress
      overlayEl.style.opacity = String(0.6 * menuProgress.value)
    }
  }

  touchEndHandler = (e) => {
    if (edge === 'none') return

    // 左エッジ終了：戻る or キャンセル
    if (edge === 'left') {
      if (!dragging) {
        edge = 'none'
        return
      }
      const changed = e.changedTouches[0]
      const dx = changed.clientX - startX
      if (dx > TRIGGER) {
        shellEl.style.transition = 'transform 0.12s ease-out'
        shellEl.style.transform = `translateX(${MAX_SHIFT + 10}px)`
        overlayEl.style.transition = 'opacity 0.12s ease-out'
        overlayEl.style.opacity = showMenu.value ? '0.6' : '0.2'

        setTimeout(() => {
          resetPositionLeft()
          router.back()
        }, 120)
      } else {
        resetPositionLeft()
      }
    }

    // 右エッジ終了：閾値で開閉を決める
    if (edge === 'right') {
      isDraggingRight.value = false
      if (menuProgress.value > 0.3) {
        openMenu()
      } else {
        closeMenu()
      }
    }

    dragging = false
    edge = 'none'
  }

  window.addEventListener('touchstart', touchStartHandler, { passive: true })
  window.addEventListener('touchmove', touchMoveHandler, { passive: false })
  window.addEventListener('touchend', touchEndHandler, { passive: true })
  window.addEventListener('touchcancel', touchEndHandler, { passive: true })
})

onBeforeUnmount(() => {
  PullToRefresh.destroyAll()
  if (touchStartHandler) window.removeEventListener('touchstart', touchStartHandler)
  if (touchMoveHandler) window.removeEventListener('touchmove', touchMoveHandler)
  if (touchEndHandler) {
    window.removeEventListener('touchend', touchEndHandler)
    window.removeEventListener('touchcancel', touchEndHandler)
  }
  PullToRefresh.destroyAll()
})
</script>

<template>
  <div id="swipe-shell" ref="shell">
    <div
      id="swipe-overlay"
      ref="overlay"
      :class="{ 'overlay-active': showMenu }"
      @click="closeMenu"
    ></div>

    <LoadingSpinner :show="appLoading" />

    <div class="app-container" :class="{ 'ios-extra-padding': isIOS }">
      <!-- <header
        class="header position-fixed top-0 w-100 border-top footer-app-container p-3 pb-0"
        :class="{ 'ios-extra-padding': isIOS }"
        style="z-index: 30;"
      >
        <div class="d-flex justify-content-between p-2">
          <router-link to="/logs" class="btn btn-sm df-center">
            <img src="/icon.svg" height="40" alt="">
          </router-link>
          <div class="d-flex gap-2">
            <router-link to="/works" class="btn btn-sm df-center">
              <IconCategory :size="32" />
            </router-link>
            <router-link 
              v-if="isGuest"
              to="/login"
              class="btn btn-sm df-center"
              title="ログイン"
            >
              <IconLogin :size="28" />
            </router-link>
            <button
              v-else
              type="button"
              class="btn btn-sm df-center position-relative"
              @click="openMenu"
              :title="userDisplayName"
            >
              <IconUser :size="28" />
            </button>
          </div>
        </div>
      </header> -->

      <div :class="{ 'web-extra-margin': !isIOS }">
        <router-view />
      </div>

      <div
        ref="sideMenu"
        class="menu-content side-menu py-3"
        :style="sideMenuStyle"
        @click.stop
      >
        <div
        class="d-flex flex-column justify-content-between"
        :class="{ 'ios-extra-padding': isIOS }"
        style="height: 100vh;">
          <nav class="menu-nav px-2">
            <ul>
              <li class="border-bottom"><router-link to="/logs" @click="closeMenu">ホーム</router-link></li>
              <li class="border-bottom"><router-link to="/logs/new" @click="closeMenu">観劇を記録する</router-link></li>
              <li class="border-bottom"><router-link to="/works" @click="closeMenu">作品一覧</router-link></li>
              <li class="border-bottom"><router-link to="/works/new" @click="closeMenu">作品を登録する</router-link></li>
              <li class="border-bottom"><router-link to="/settings" @click="closeMenu">設定</router-link></li>
              <li class="border-bottom"><router-link to="/contact" @click="closeMenu">お問い合わせ</router-link></li>
              <li class="border-bottom">
                <router-link v-if="isGuest" to="/login" @click="closeMenu">ログイン</router-link>
                <button
                  v-else
                  type="button"
                  class="btn btn-link text-decoration-none w-100 text-start"
                  style="color: #333;"
                  @click="logout"
                >
                  ログアウト
                </button>
              </li>
              <li>

              </li>
            </ul>
          </nav>
          <div class="wrap d-flex flex-column px-2">
            <div v-if="!isGuest" class="mb-3">
              <button
                type="button"
                class="btn btn-sm btn-outline-danger w-100 text-danger"
                style="color: #333;"
                @click="logout"
              >
                ログアウト
              </button>
            </div>
            <div v-else class="mb-3">
              <button
                type="button"
                class="btn btn-sm btn-outline-primary w-100 text-primary"
                style="color: #333;"
                @click="$router.push('/login')"
              >
                ログイン
              </button>
            </div>
            <div class="d-flex justify-content-between align-items-end">
              <div class="small">
                <router-link to="/about-contents" @click="closeMenu">コンテンツについて</router-link>
              </div>
              <div class="d-flex justify-content-end">
                <a class="ms-0" href="https://studio-shindra.com" target="_blank">
                  <img src="/shindra-icon-bk.svg" width="24" alt="studio-shindra">
                </a>
              </div>
            </div>

          </div>
        </div>
      </div>

      <footer
        class="footer bg-white position-fixed bottom-0 w-100 border-top footer-app-container p-3 pt-0"
        :class="{ 'ios-extra-padding': isIOS }"
        style="z-index: 19;"
      >
        <div class="d-flex align-items-center justify-content-between p-2">
          <router-link 
            to="/logs"
            class="btn btn-sm df-center position-relative"
            :title="currentUser?.username"
            style="width: 48px; height: 48px; border-radius: 50%; overflow: hidden; padding: 0; border: none; background: transparent;"
          >
            <img
              v-if="profileImageUrl"
              :src="profileImageUrl"
              alt="profile"
              style="width: 100%; height: 100%; object-fit: cover;"
            />
            <div
              v-else
              class="df-center fw-bold w-100 h-100 bg-light fs-5"
              style="color: #666;"
            >
              {{ profileInitial }}
            </div>
          </router-link>

          <div class="df-center gap-2">
            <router-link to="/works" class="btn btn-sm df-center">
              <IconCategory :size="32" />
            </router-link>
            <button @click="openMenu" class="btn btn-sm df-center">
              <img src="/icon.svg" height="40" alt="">
            </button>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style lang="scss">
#swipe-shell {
  position: relative;
  overflow: hidden;
  touch-action: pan-y;
  min-height: 100vh;
}

#swipe-overlay {
  pointer-events: none;
  position: fixed;
  inset: 0;
  min-height: 100vh;
  background: black;
  opacity: 0;
  transition: opacity 0.15s ease-out;
  z-index: 20;
}


#swipe-overlay.overlay-active {
  pointer-events: auto;
}

.app-container {
  position: relative;
  // z-index: 1;
  padding-top: env(safe-area-inset-top);
  padding-bottom: calc(env(safe-area-inset-bottom) + 24px + 50px); // 50px for AdMob footer
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

.app-container.ios-extra-padding {
  padding-top: calc(env(safe-area-inset-top) + 1rem);
}

.header.ios-extra-padding {
  padding-top: 3rem !important;
}

.web-extra-margin {
  margin-bottom: 80px; // Space for AdMob footer
}

.footer-app-container {
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* メニュー本体 */
.menu-content{
  &.side-menu {
    position: fixed;
    inset: 0 0 0 auto;
    width: 70vw;
    max-width: 320px;
    background: #fff;
    display: flex;
    flex-direction: column;
    z-index: 31;
    transform: translateX(100%); /* 初期状態：画面外 */
    .ios-extra-padding {
      padding-top: calc(env(safe-area-inset-top) + 1rem);
      padding-bottom: calc(env(safe-area-inset-bottom) + 1rem);
      padding-left: env(safe-area-inset-left);
    }
  }
}

/* メニューナビゲーション */
.menu-nav ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.menu-nav li {
  margin-bottom: 0.75rem;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.menu-nav li:hover {
  transform: translateX(4px);
}

.menu-nav a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.menu-nav a:hover {
  background-color: #f0f0f0;
}

/* スライダーコンテナ用（必要箇所でクラス付与） */
.slider-container {
  touch-action: pan-y;
}
</style>