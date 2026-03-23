import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, isCapacitor, getToken, setToken, clearToken } from '@/lib/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const isShopUser = computed(
    () => user.value && (user.value.role === 'shop' || user.value.role === 'admin'),
  )

  async function fetchMe() {
    try {
      if (isCapacitor && !getToken()) {
        // Token がなければ未ログイン（旧 Session に依存しない）
        user.value = null
        return
      }
      const path = isCapacitor ? '/api/mobile/auth/me/' : '/api/auth/me/'
      user.value = await api.get(path)
    } catch {
      user.value = null
      if (isCapacitor) clearToken()
    }
  }

  async function login(username, password) {
    if (isCapacitor) {
      const data = await api.post('/api/mobile/auth/login/', { username, password })
      setToken(data.token)
      user.value = data.user
      return data
    }
    const data = await api.post('/api/auth/login/', { username, password })
    user.value = data.user || data
    return data
  }

  async function register(payload) {
    if (isCapacitor) {
      const data = await api.post('/api/mobile/auth/register/', payload)
      setToken(data.token)
      user.value = data.user
      return data
    }
    const data = await api.post('/api/auth/register/', payload)
    user.value = data.user || data
    return data
  }

  async function logout() {
    if (isCapacitor) {
      try {
        await api.post('/api/mobile/auth/logout/')
      } catch {
        /* token already invalid */
      }
      clearToken()
    } else {
      await api.post('/api/auth/logout/')
    }
    user.value = null
  }

  async function deleteAccount() {
    const path = isCapacitor ? '/api/mobile/auth/me/' : '/api/auth/me/'
    await api.delete(path)
    if (isCapacitor) clearToken()
    user.value = null
  }

  return { user, isAuthenticated, isShopUser, fetchMe, login, register, logout, deleteAccount }
})
