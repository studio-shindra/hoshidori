const isCapacitor = window.location.protocol === 'capacitor:'
  || window.location.protocol === 'ionic:'
const BASE = isCapacitor
  ? 'https://hoshidori-67b44bed2d10.herokuapp.com'
  : (import.meta.env.VITE_API_BASE_URL || '')

function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')
  return v ? v.pop() : ''
}

async function request(method, path, body = null) {
  const opts = {
    method,
    credentials: 'include',
    headers: {},
  }
  if (body) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  if (method !== 'GET') {
    opts.headers['X-CSRFToken'] = getCookie('csrftoken')
  }
  if (isCapacitor) {
    opts.headers['X-Requested-With'] = 'capacitor'
  }
  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    const err = new Error(`API ${res.status}`)
    err.status = res.status
    try {
      err.data = await res.json()
    } catch {
      /* empty */
    }
    throw err
  }
  if (res.status === 204) return null
  return res.json()
}

async function upload(path, formData) {
  const headers = { 'X-CSRFToken': getCookie('csrftoken') }
  if (isCapacitor) {
    headers['X-Requested-With'] = 'capacitor'
  }
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers,
    body: formData,
  })
  if (!res.ok) {
    const err = new Error(`API ${res.status}`)
    err.status = res.status
    try {
      err.data = await res.json()
    } catch {
      /* empty */
    }
    throw err
  }
  return res.json()
}

// Simple in-memory cache for GET requests (30s TTL)
const cache = new Map()
const CACHE_TTL = 30000

function getCached(path) {
  const entry = cache.get(path)
  if (entry && Date.now() - entry.time < CACHE_TTL) {
    return entry.data
  }
  cache.delete(path)
  return null
}

function setCache(path, data) {
  cache.set(path, { data, time: Date.now() })
}

function invalidateCache() {
  cache.clear()
}

export const api = {
  get: async (path) => {
    const cached = getCached(path)
    if (cached) return cached
    const data = await request('GET', path)
    setCache(path, data)
    return data
  },
  post: async (path, body) => {
    invalidateCache()
    return request('POST', path, body)
  },
  patch: async (path, body) => {
    invalidateCache()
    return request('PATCH', path, body)
  },
  delete: async (path) => {
    invalidateCache()
    return request('DELETE', path)
  },
  upload: async (path, formData) => {
    invalidateCache()
    return upload(path, formData)
  },
}
