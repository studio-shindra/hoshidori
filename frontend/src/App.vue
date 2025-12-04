<script setup>
import { IconCategory } from '@tabler/icons-vue'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdMob, BannerAdSize, BannerAdPosition } from '@capacitor-community/admob'
import { Capacitor } from '@capacitor/core'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()
const appLoading = ref(true)
const isIOS = Capacitor.getPlatform() === 'ios'

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
        <router-link to="/logs" class="btn btn-sm">
          <img src="/icon.svg" height="40" alt="">
        </router-link>
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
  </div>
</template>

<style>
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
  margin-top: 80px !important;
}

.footer-app-container{
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}
</style>