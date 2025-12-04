<script setup>
import { IconCategory } from '@tabler/icons-vue'
import { VueFinalModal } from 'vue-final-modal'
import 'vue-final-modal/style.css'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdMob, BannerAdSize, BannerAdPosition } from '@capacitor-community/admob'
import { Capacitor } from '@capacitor/core'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()

const showDrawer = ref(false)
const appLoading = ref(true)
const isIOS = Capacitor.getPlatform() === 'ios'

function closeDrawer() {
  showDrawer.value = false
}

// 環境に応じてテスト/本番を自動切り替え（development: テスト / production: 本番）
const USE_TEST_ADS = import.meta.env.DEV

const ADMOB_IDS = {
  // .envから読み込み（未設定時はGoogleのテストID/提供済み本番IDにフォールバック）
  test: import.meta.env.VITE_ADMOB_BANNER_TEST_ID || 'ca-app-pub-3940256099942544/2934735716',
  production: import.meta.env.VITE_ADMOB_BANNER_PROD_ID || 'ca-app-pub-6836938378520436/7549822530'
}

onMounted(async () => {
  try {
    await AdMob.initialize()
    
    await AdMob.showBanner({
      adId: USE_TEST_ADS ? ADMOB_IDS.test : ADMOB_IDS.production,
      adSize: BannerAdSize.BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
      margin: 0,
    })
  } catch (error) {
    console.error('AdMob initialization error:', error)
  }

  // 最低1.5秒は表示（バウンスアニメーションを見せる）
  setTimeout(() => {
    appLoading.value = false
  }, 1500)
})

onUnmounted(() => {
  // クリーンアップ
})
</script>

<template>
  <LoadingSpinner :show="appLoading" />
  <div class="app-container" :class="{ 'ios-extra-padding': isIOS }">
    <header
      class="header position-fixed top-0 w-100 border-top footer-app-container p-3 pb-0"
      :class="{ 'ios-extra-padding': isIOS }"
      style="z-index: 999;">
      <div class="d-flex justify-content-between p-2">
        <button type="button" class="btn btn-sm df-center" @click="showDrawer = true">
          <img src="/icon.svg" height="40" alt="">
        </button>
        <router-link to="/works" class="btn btn-sm df-center">
          <IconCategory :size="32" />
        </router-link>
      </div>
      <!-- <div class="text-center mt-1" style="font-size: 0.65rem; color: #999;">
        ※アプリ応援のため広告が表示されることがあります
      </div> -->
    </header>
    <div :class="{ 'web-extra-margin': !isIOS }">
      <router-view />
    </div>
    <!-- ドロワー本体 -->
    <VueFinalModal
      v-model="showDrawer"
      content-class="drawer-content"
      overlay-class="drawer-overlay"
      content-transition="vfm-slide-right"
      overlay-transition="vfm-fade"
      :click-to-close="true"
      :esc-to-close="true"
      :swipe-to-close="'right'"
      :lock-scroll="true"
    >
    
    <div
     class="py-4 d-flex flex-column justify-content-between"
     style="height: 100vh;">
      <nav class="drawer-nav px-2">
        <ul :class="{ 'ios-extra-padding': isIOS }">
          <li class="border-bottom"><router-link to="/logs" @click="closeDrawer">ホーム</router-link></li>
          <li class="border-bottom"><router-link to="/logs/new" @click="closeDrawer">観劇を記録する</router-link></li>
          <li class="border-bottom"><router-link to="/works" @click="closeDrawer">作品一覧</router-link></li>
          <li class="border-bottom"><router-link to="/works/new" @click="closeDrawer">作品を登録する</router-link></li>
          <li class="border-bottom"><router-link to="/contact" @click="closeDrawer">お問い合わせ</router-link></li>
        </ul>
      </nav>
      <div class="wrap d-flex flex-column px-2">
        <div class="small">
          <router-link to="/about-contents" @click="closeDrawer">コンテンツについて</router-link>
        </div>
        <div class="d-flex justify-content-end">
          <a class="ms-0" href="https://studio-shindra.com" target="_blank">
            <img src="/shindra-icon-bk.svg" width="24" alt="studio-shindra">
          </a>
        </div>
      </div>
    </div>
    </VueFinalModal>
  </div>
</template>

<style lang="scss">
.app-container {
  /* ヘッダーにバナーを置くため、セーフエリア + ヘッダー相当の余白 */
  padding-top: env(safe-area-inset-top);
  padding-bottom: calc(env(safe-area-inset-bottom) + 24px);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* iOSの場合のみ追加の余白 */
.app-container.ios-extra-padding {
  padding-top: calc(env(safe-area-inset-top) + 3rem);
}

.header.ios-extra-padding{
  padding-top: 3rem !important;
}

.web-extra-margin{
  margin-top: 64px !important;
}

.footer-app-container{
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}

/* ドロワー用 */
.drawer-overlay {
  background: rgba(0, 0, 0, 0.4);
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-content {
  position: fixed;
  inset: 0 0 0 auto;
  width: 70vw;
  background: #fff;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    &.ios-extra-padding {
    padding-top: calc(env(safe-area-inset-top) + 2rem);
  }
}


/* スライドアニメーション */
.vfm-slide-right-enter-active,
.vfm-slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.vfm-slide-right-enter-from {
  transform: translateX(100%);
}

.vfm-slide-right-leave-to {
  transform: translateX(100%);
}

/* オーバーレイフェード */
.vfm-fade-enter-active,
.vfm-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.vfm-fade-enter-from,
.vfm-fade-leave-to {
  opacity: 0;
}

.drawer-nav ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.drawer-nav li {
  margin-bottom: 0.75rem;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.drawer-nav li:hover {
  transform: translateX(4px);
}

.drawer-nav a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.drawer-nav a:hover {
  background-color: #f0f0f0;
}

</style>