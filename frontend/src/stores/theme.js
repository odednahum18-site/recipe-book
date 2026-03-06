import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light'
  }),

  getters: {
    isDark: (state) => state.theme === 'dark'
  },

  actions: {
    initTheme() {
      const stored = localStorage.getItem('recipe-book-theme')
      this.theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      this.applyTheme()
    },

    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      localStorage.setItem('recipe-book-theme', this.theme)
      this.applyTheme()
    },

    applyTheme() {
      document.documentElement.classList.toggle('dark', this.theme === 'dark')
    }
  }
})
