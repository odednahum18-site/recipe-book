import { defineStore } from 'pinia'
import api from '@/api'

const AUTH_MODE = import.meta.env.VITE_AUTH_MODE || 'jwt'

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
    isEditor: (state) => ['admin', 'editor'].includes(state.user?.role),
    isFirebaseAuth: () => AUTH_MODE === 'firebase'
  },

  actions: {
    initAuth() {
      if (AUTH_MODE === 'firebase') {
        this._initFirebaseAuth()
      } else {
        const token = localStorage.getItem('recipe-book-token')
        const user = localStorage.getItem('recipe-book-user')
        if (token && user) {
          this.token = token
          this.user = JSON.parse(user)
        }
      }
    },

    async _initFirebaseAuth() {
      const { auth } = await import('@/firebase')
      const { onAuthStateChanged } = await import('firebase/auth')
      onAuthStateChanged(auth, async (firebaseUser) => {
        if (firebaseUser) {
          const idToken = await firebaseUser.getIdToken()
          this.token = idToken
          localStorage.setItem('recipe-book-token', idToken)
          try {
            const result = await api.firebaseLogin()
            this.user = result.user
            localStorage.setItem('recipe-book-user', JSON.stringify(result.user))
          } catch {
            this.logout()
          }
        } else {
          this.token = null
          this.user = null
          localStorage.removeItem('recipe-book-token')
          localStorage.removeItem('recipe-book-user')
        }
      })
    },

    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        if (AUTH_MODE === 'firebase') {
          const { auth } = await import('@/firebase')
          const { signInWithEmailAndPassword } = await import('firebase/auth')
          const credential = await signInWithEmailAndPassword(auth, username, password)
          const idToken = await credential.user.getIdToken()
          this.token = idToken
          localStorage.setItem('recipe-book-token', idToken)
          const result = await api.firebaseLogin()
          this.user = result.user
          localStorage.setItem('recipe-book-user', JSON.stringify(result.user))
        } else {
          const result = await api.login(username, password)
          this.token = result.access_token
          this.user = result.user
          localStorage.setItem('recipe-book-token', result.access_token)
          localStorage.setItem('recipe-book-user', JSON.stringify(result.user))
        }
        return true
      } catch (e) {
        this.error = e.message || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async googleLogin(credential) {
      this.loading = true
      this.error = null
      try {
        const result = await api.googleLogin(credential)
        this.token = result.access_token
        this.user = result.user
        localStorage.setItem('recipe-book-token', result.access_token)
        localStorage.setItem('recipe-book-user', JSON.stringify(result.user))
        return true
      } catch (e) {
        this.error = e.message || 'Google login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout() {
      if (AUTH_MODE === 'firebase') {
        try {
          const { auth } = await import('@/firebase')
          const { signOut } = await import('firebase/auth')
          await signOut(auth)
        } catch { /* ignore */ }
      }
      this.token = null
      this.user = null
      localStorage.removeItem('recipe-book-token')
      localStorage.removeItem('recipe-book-user')
    }
  }
})
