import { defineStore } from 'pinia'
import i18n from '@/i18n'

export const useLocaleStore = defineStore('locale', {
  state: () => ({
    locale: 'he'
  }),

  getters: {
    isHebrew: (state) => state.locale === 'he',
    direction: (state) => state.locale === 'he' ? 'rtl' : 'ltr'
  },

  actions: {
    initLocale() {
      const stored = localStorage.getItem('recipe-book-locale')
      this.locale = stored || 'he'
      this.applyLocale()
    },

    toggleLocale() {
      this.locale = this.locale === 'he' ? 'en' : 'he'
      localStorage.setItem('recipe-book-locale', this.locale)
      this.applyLocale()
    },

    applyLocale() {
      i18n.global.locale.value = this.locale
      document.documentElement.lang = this.locale
      document.documentElement.dir = this.direction
    }
  }
})
