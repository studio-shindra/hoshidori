<script setup>
import { IconSearch } from '@tabler/icons-vue'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdMob, BannerAdSize, BannerAdPosition } from '@capacitor-community/admob'

const router = useRouter()

// 環境に応じてテスト/本番を自動切り替え（development: テスト / production: 本番）
const USE_TEST_ADS = import.meta.env.DEV

const ADMOB_IDS = {
  // .envから読み込み（未設定時はGoogleのテストID/提供済み本番IDにフォールバック）
  test: import.meta.env.VITE_ADMOB_BANNER_TEST_ID || 'ca-app-pub-3940256099942544/2934735716',
  production: import.meta.env.VITE_ADMOB_BANNER_PROD_ID || 'ca-app-pub-6836938378520436/7549822530'
}

// スワイプジェスチャー検知用
let touchStartX = 0
let touchStartY = 0
let touchEndX = 0
let touchEndY = 0

function handleTouchStart(e) {
  touchStartX = e.changedTouches[0].screenX
  touchStartY = e.changedTouches[0].screenY
}

function handleTouchEnd(e) {
  touchEndX = e.changedTouches[0].screenX
  touchEndY = e.changedTouches[0].screenY
  handleSwipeGesture()
}

function handleSwipeGesture() {
  const diffX = touchEndX - touchStartX
  const diffY = touchEndY - touchStartY
  const minSwipeDistance = 100
  
  // 縦方向の移動が大きい場合はスワイプとみなさない（スクロール優先）
  if (Math.abs(diffY) > Math.abs(diffX)) {
    return
  }
  
  // 横スワイプの判定
  if (Math.abs(diffX) > minSwipeDistance) {
    if (diffX > 0) {
      // 右スワイプ → /works へ
      router.push('/works')
    } else {
      // 左スワイプ → /logs へ
      router.push('/logs')
    }
  }
}

onMounted(async () => {
  try {
    await AdMob.initialize()
    
    await AdMob.showBanner({
      adId: USE_TEST_ADS ? ADMOB_IDS.test : ADMOB_IDS.production,
      adSize: BannerAdSize.BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
      margin: 0, // 上部に配置（セーフエリアはCSSで確保）
    })
  } catch (error) {
    console.error('AdMob initialization error:', error)
  }
  
  // スワイプジェスチャーリスナーを登録
  document.addEventListener('touchstart', handleTouchStart, false)
  document.addEventListener('touchend', handleTouchEnd, false)
})

onUnmounted(() => {
  // クリーンアップ
  document.removeEventListener('touchstart', handleTouchStart)
  document.removeEventListener('touchend', handleTouchEnd)
})
</script>

<template>
  <div class="app-container">
    <header
      class="position-fixed top-0 w-100 border-top footer-app-container p-3 pb-0"
      style="z-index: 999;">
      <div class="d-flex justify-content-between p-2">
        <router-link to="/logs" class="btn btn-sm">
          <img src="/icon.svg" height="40" alt="">
        </router-link>
        <router-link to="/works" class="btn btn-sm df-center">
          <IconSearch />
        </router-link>
      </div>
      <!-- <div class="text-center mt-1" style="font-size: 0.65rem; color: #999;">
        ※アプリ応援のため広告が表示されることがあります
      </div> -->
    </header>
    <div>
      <router-view />
    </div>
  </div>
</template>

<style>
.app-container {
  /* ヘッダーにバナーを置くため、セーフエリア + ヘッダー相当の余白 */
  padding-top: calc(env(safe-area-inset-top) + 24px);
  padding-bottom: calc(env(safe-area-inset-bottom) + 24px);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
.footer-app-container{
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}
</style>