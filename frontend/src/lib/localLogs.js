const STORAGE_KEY = 'hoshidori_local_logs_v1'

function readAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch (_) {
    return []
  }
}

function saveAll(logs) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(logs))
}

function normalizePayload(payload) {
  const now = new Date().toISOString()
  const watchedAt = payload.watched_at || payload.watchedDate || null

  // work オブジェクトを保持（actors, tags 含む）
  let work = payload.work || null
  
  // payload.tags がなく、work に tags があれば、work.tags から文字列配列を抽出
  let tags = payload.tags || []
  if (!tags.length && work && Array.isArray(work.tags)) {
    tags = work.tags.map(t => typeof t === 'string' ? t : (t.name || ''))
  }

  return {
    id: payload.id || Date.now(),
    work_id: payload.work_id || payload.workId || null,
    work: work,
    run: payload.run || null,
    seat: payload.seat || '',
    memo: payload.memo || '',
    rating: payload.rating ?? null,
    tags: tags,
    watched_at: watchedAt,
    watchedDate: watchedAt,
    created_at: payload.created_at || now,
    updated_at: payload.updated_at || now,
  }
}

export function isGuestUser() {
  return !localStorage.getItem('hoshidori_token')
}

export function listLocalLogs() {
  return readAll()
}

export function getLocalLog(id) {
  const logs = readAll()
  return logs.find((log) => String(log.id) === String(id)) || null
}

export function createLocalLog(payload) {
  const logs = readAll()
  const log = normalizePayload(payload)
  logs.unshift(log)
  saveAll(logs)
  return log
}

export function updateLocalLog(id, payload) {
  const logs = readAll()
  const idx = logs.findIndex((log) => String(log.id) === String(id))
  if (idx === -1) return null

  // 既存の work オブジェクトを保持しつつ、新しいペイロードで更新
  const existing = logs[idx]
  const merged = {
    ...existing,
    ...payload,
    // work が新たに渡された場合はそれを使う、なければ既存を保持
    work: payload.work || existing.work,
    id: existing.id
  }

  const updated = {
    ...normalizePayload(merged),
    updated_at: new Date().toISOString(),
  }
  logs[idx] = updated
  saveAll(logs)
  return updated
}

export function deleteLocalLog(id) {
  const logs = readAll()
  const next = logs.filter((log) => String(log.id) !== String(id))
  saveAll(next)
}
