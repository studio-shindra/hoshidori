// frontend/src/apiClient.js
const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '') // 末尾のスラッシュを削除

// ===== キャッシュ機能 =====
const apiCache = new Map()
// key: "GET:/api/logs/" みたいな文字列
// value: { data, time }

function makeCacheKey(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  return `${method}:${path}`
}

/**
 * 一定時間だけキャッシュする版の request
 * @param {string} path - "/api/logs/" みたいなパス
 * @param {object} options - fetch のオプション
 * @param {object} cacheOptions - { ttlMs: number, force: boolean }
 */
export async function requestWithCache(path, options = {}, cacheOptions = {}) {
  const { ttlMs = 60_000, force = false } = cacheOptions
  const key = makeCacheKey(path, options)

  if (!force) {
    const cached = apiCache.get(key)
    if (cached && Date.now() - cached.time < ttlMs) {
      console.log('[HOSHIDORI] cache hit:', key)
      return cached.data
    }
  }

  const data = await request(path, options)
  apiCache.set(key, { data, time: Date.now() })
  return data
}

function getAccessToken() {
  // ログイン時に localStorage.setItem('hoshidori_token', access) してある想定
  const t = localStorage.getItem('hoshidori_token') || ''
  // 誤ってrefreshを保存してしまった場合に備え、ペイロードを確認
  if (t) {
    const parts = t.split('.')
    if (parts.length === 3) {
      try {
        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
        if (payload && payload.token_type === 'refresh') {
          // refreshが入っている場合はアクセストークンとしては無効扱い
          return ''
        }
      } catch (_) {
        // 解析失敗時はそのまま返す
      }
    }
  }
  return t
}

function getRefreshToken() {
  return localStorage.getItem('hoshidori_refresh') || ''
}

function setAccessToken(token) {
  localStorage.setItem('hoshidori_token', token)
}

function clearTokens() {
  localStorage.removeItem('hoshidori_token')
  localStorage.removeItem('hoshidori_refresh')
}

async function refreshAccessToken() {
  const refresh = getRefreshToken()
  if (!refresh) throw new Error('No refresh token')

  const res = await fetch(`${baseUrl}/api/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Refresh failed: ${res.status}`)
  }

  const data = await res.json()
  if (!data.access) throw new Error('No access token returned')
  setAccessToken(data.access)
  return data.access
}

export async function request(path, options = {}, _retried = false) {
  const url = `${baseUrl}${path}`
  
  console.log('[HOSHIDORI] API request:', url, options)
  console.log('[HOSHIDORI] baseUrl:', baseUrl)

  const headers = new Headers({
    ...(options.headers || {}),
  })

  let token = getAccessToken()
  // アクセストークンが無いがリフレッシュがある場合は事前に更新を試みる
  if (!token && getRefreshToken()) {
    try {
      token = await refreshAccessToken()
    } catch (_) {
      // 更新失敗時は後続の通常フローへ
    }
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  // JSON送信がデフォ（ただし既に Content-Type が指定されていればそれを尊重）
  if (!headers.has('Content-Type')) {
    if (!options.body || typeof options.body === 'string') {
      headers.set('Content-Type', 'application/json')
    }
  }

  let res = await fetch(url, {
    ...options,
    headers,
    credentials: 'omit', // JWT in header only, no cookies
  }).catch((e) => {
    console.error('[HOSHIDORI] Fetch error:', e)
    throw e
  })
  
  console.log('[HOSHIDORI] API response:', url, res.status)

  // 期限切れなどで401の場合は1回だけトークン更新してリトライ
  if (res.status === 401 && !_retried) {
    try {
      await refreshAccessToken()
      // 更新後にAuthorizationヘッダーを差し替えて再実行
      const newHeaders = new Headers(headers)
      newHeaders.set('Authorization', `Bearer ${getAccessToken()}`)
      res = await fetch(url, { ...options, headers: newHeaders, credentials: 'omit' })
    } catch (e) {
      clearTokens()
      const text = await res.text().catch(() => '')
      throw new Error(`API error: 401 ${text || (e && e.message) || 'Unauthorized'}`)
    }
  }

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    console.error('[HOSHIDORI] API error body:', text)
    throw new Error(`API error: ${res.status} ${text}`)
  }

  const contentType = res.headers.get('Content-Type') || ''
  if (contentType.includes('application/json')) {
    return res.json()
  }
  return res.text()
}

export function fetchWorks(params = {}) {
  const query = new URLSearchParams(params)
  const qs = query.toString() ? `?${query.toString()}` : ''
  return requestWithCache(`/api/works/${qs}`, {}, { ttlMs: 5 * 60_000 }) // 5分キャッシュ
}

export function fetchWorkSchedule(workId) {
  return requestWithCache(`/api/works/${workId}/schedule/`, {}, { ttlMs: 60_000 })
}

export function fetchMyLogs({ force = false } = {}) {
  return requestWithCache('/api/logs/', {}, {
    ttlMs: 60_000,  // 1分以内ならキャッシュを返す
    force,
  })
}

export function createLog(payload) {
  return request('/api/logs/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteLog(id) {
  return request(`/api/logs/${id}/`, {
    method: 'DELETE',
  })
}