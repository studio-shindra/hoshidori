// src/authState.js
import { ref } from 'vue'
import { getLocalDisplayName, getLocalProfileInitial, getLocalProfileImageUrl } from '@/lib/localSettings'

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
  if (!currentUser.value) {
    // ゲストユーザー：ローカル設定から取得
    return getLocalProfileInitial()
  }
  // ログインユーザー：サーバーのデータから取得
  const username = currentUser.value.username || currentUser.value.first_name || 'U'
  return username.charAt(0).toUpperCase()
}

export function getDisplayName() {
  if (!currentUser.value) {
    // ゲストユーザー：ローカル設定から取得
    const localName = getLocalDisplayName()
    return localName || 'ゲスト'
  }
  // ログインユーザー：サーバーのデータから取得
  return currentUser.value.username || currentUser.value.first_name || 'User'
}

export function getProfileImageUrl() {
  if (!currentUser.value) {
    // ゲストユーザー：ローカル設定から取得
    return getLocalProfileImageUrl()
  }
  // ログインユーザー：サーバーのデータから取得
  return currentUser.value.profile_image || null
}