// AdMob インタースティシャル広告のヘルパー関数
import { AdMob } from '@capacitor-community/admob'

/**
 * ログ保存成功時にカウントを増やし、3回に1回だけインタースティシャル広告を表示
 */
export async function onLogSaveSuccess() {
  try {
    // 保存回数をカウント
    const raw = window.localStorage.getItem('logSaveCount') || '0'
    const count = Number(raw) + 1
    window.localStorage.setItem('logSaveCount', String(count))

    console.log(`[HOSHIDORI] ログ保存回数: ${count}回目`)

    // 3回に1回だけインタースティシャルを表示
    if (count % 3 === 0) {
      console.log('[HOSHIDORI] インタースティシャル広告を表示します')
      await loadAndShowInterstitial()
    }
  } catch (error) {
    console.error('[HOSHIDORI] インタースティシャル広告エラー:', error)
    // エラーが出てもユーザー操作はブロックしない
  }
}

/**
 * インタースティシャル広告をロードして表示
 */
async function loadAndShowInterstitial() {
  try {
    // 環境に応じてテスト/本番IDを切り替え
    const USE_TEST_ADS = import.meta.env.DEV
    const INTERSTITIAL_AD_ID = USE_TEST_ADS
      ? (import.meta.env.VITE_ADMOB_INTERSTITIAL_TEST_ID || 'ca-app-pub-3940256099942544/4411468910')
      : (import.meta.env.VITE_ADMOB_INTERSTITIAL_PROD_ID || 'ca-app-pub-6836938378520436/1564790695')

    console.log('[HOSHIDORI] インタースティシャル広告ID:', INTERSTITIAL_AD_ID)

    // 広告を準備
    await AdMob.prepareInterstitial({
      adId: INTERSTITIAL_AD_ID,
    })

    console.log('[HOSHIDORI] インタースティシャル広告の準備完了')

    // 広告を表示
    await AdMob.showInterstitial()

    console.log('[HOSHIDORI] インタースティシャル広告を表示しました')
  } catch (error) {
    // ロード失敗・タイムアウト時は何も表示せず、ユーザー操作もブロックしない
    console.error('[HOSHIDORI] インタースティシャル広告の表示に失敗:', error)
  }
}
