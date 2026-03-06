import { defineStore } from 'pinia'
import api from '@/api'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loading: false,
    error: null
  }),

  getters: {
    getCategoryById: (state) => (id) => state.categories.find(c => c.id === id),
    getCategoryBySlug: (state) => (slug) => state.categories.find(c => c.slug === slug)
  },

  actions: {
    async fetchCategories() {
      this.loading = true
      try {
        this.categories = await api.getCategories()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    }
  }
})
