import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/lib/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const isShopUser = computed(
    () => user.value && (user.value.role === 'shop' || user.value.role === 'admin'),
  )

  async function fetchMe() {
    try {
      user.value = await api.get('/api/auth/me/')
    } catch {
      user.value = null
    }
  }

  async function login(username, password) {
    const data = await api.post('/api/auth/login/', { username, password })
    user.value = data.user || data
    return data
  }

  async function register(payload) {
    const data = await api.post('/api/auth/register/', payload)
    user.value = data.user || data
    return data
  }

  async function logout() {
    await api.post('/api/auth/logout/')
    user.value = null
  }

  return { user, isAuthenticated, isShopUser, fetchMe, login, register, logout }
})
