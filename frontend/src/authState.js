// src/authState.js
import { ref } from 'vue'

export const currentUser = ref(null)
export const authReady = ref(false)

async function fetchUserProfile() {
  try {
    const token = localStorage.getItem('hoshidori_token')
    if (!token) return null

    const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
    const res = await fetch(`${baseUrl}/api/auth/user/`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (!res.ok) return null
    return res.json()
  } catch (_) {
    return null
  }
}

export async function initAuth() {
  // ローカルにJWTがあれば簡易的にログイン状態とみなす
  const token = localStorage.getItem('hoshidori_token')
  if (token) {
    const userProfile = await fetchUserProfile()
    currentUser.value = { token, ...userProfile }
  } else {
    currentUser.value = null
  }
  authReady.value = true
}

export function getProfileInitial() {
  if (!currentUser.value) return '?'
  const username = currentUser.value.username || currentUser.value.first_name || '?'
  return username.charAt(0).toUpperCase()
}