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
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
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

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path) => request('DELETE', path),
  upload: (path, formData) => upload(path, formData),
}
