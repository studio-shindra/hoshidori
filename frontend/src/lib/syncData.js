import { listLocalLogs } from './localLogs'
import { getLocalDisplayName, getLocalProfileImageUrl } from './localSettings'
import { request } from '@/apiClient'

/**
 * ログイン後にローカルデータをサーバーに同期
 */
export async function syncLocalDataToServer() {
  try {
    // 1. ローカルログをサーバーに同期
    const localLogs = listLocalLogs()
    const syncPromises = localLogs.map(log => {
      const payload = {
        work_id: log.work_id || log.work?.id,
        run: log.run,
        seat: log.seat || '',
        memo: log.memo || '',
        rating: log.rating ?? null,
        watched_at: log.watched_at || log.watchedDate,
        tags: log.tags || [],
      }
      return request('/api/logs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).catch(err => {
        console.warn('Failed to sync log:', err)
        return null
      })
    })

    await Promise.all(syncPromises)
    console.log(`${localLogs.length}件のログを同期しました`)

    // 2. ローカル設定をサーバーに反映
    const displayName = getLocalDisplayName()
    const profileImageUrl = getLocalProfileImageUrl()

    if (displayName || profileImageUrl) {
      const formData = new FormData()
      if (displayName) {
        formData.append('first_name', displayName)
      }
      
      // プロフィール画像URLがあればそのまま送信（Cloudinary URL）
      if (profileImageUrl) {
        // URLをそのまま送る場合、バックエンドで対応が必要
        // または画像をダウンロードしてFileとして送信
        console.log('Profile image URL:', profileImageUrl)
        // 今回は表示名のみ同期（画像は手動設定を推奨）
      }

      await request('/api/auth/user/', {
        method: 'PATCH',
        body: formData,
      }).catch(err => {
        console.warn('Failed to sync profile:', err)
      })

      console.log('プロフィール設定を同期しました')
    }

    return true
  } catch (err) {
    console.error('Sync failed:', err)
    return false
  }
}
