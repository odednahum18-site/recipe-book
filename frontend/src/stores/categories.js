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
    },

    async createCategory(data) {
      const result = await api.createCategory(data)
      await this.fetchCategories()
      return result
    },

    async updateCategory(id, data) {
      const result = await api.updateCategory(id, data)
      await this.fetchCategories()
      return result
    },

    async deleteCategory(id) {
      await api.deleteCategory(id)
      await this.fetchCategories()
    },

    async reorderCategories(order) {
      await api.reorderCategories(order)
      await this.fetchCategories()
    }
  }
})
