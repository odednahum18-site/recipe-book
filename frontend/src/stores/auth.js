import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    loading: false,
    error: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isEditor: (state) => ['admin', 'editor'].includes(state.user?.role)
  },

  actions: {
    initAuth() {
      const token = localStorage.getItem('recipe-book-token')
      const user = localStorage.getItem('recipe-book-user')
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
      }
    },

    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const result = await api.login(username, password)
        this.token = result.access_token
        this.user = result.user
        localStorage.setItem('recipe-book-token', result.access_token)
        localStorage.setItem('recipe-book-user', JSON.stringify(result.user))
        return true
      } catch (e) {
        this.error = e.message || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('recipe-book-token')
      localStorage.removeItem('recipe-book-user')
    }
  }
})
