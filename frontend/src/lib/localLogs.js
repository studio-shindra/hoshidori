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

  return {
    id: payload.id || Date.now(),
    work_id: payload.work_id || payload.workId || null,
    work: payload.work || null,
    run: payload.run || null,
    seat: payload.seat || '',
    memo: payload.memo || '',
    rating: payload.rating ?? null,
    tags: payload.tags || [],
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

  const updated = {
    ...logs[idx],
    ...normalizePayload({ ...logs[idx], ...payload, id: logs[idx].id }),
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
