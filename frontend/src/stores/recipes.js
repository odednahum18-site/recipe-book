import { defineStore } from 'pinia'
import api from '@/api'

export const useRecipesStore = defineStore('recipes', {
  state: () => ({
    recipes: [],
    currentRecipe: null,
    total: 0,
    page: 1,
    pageSize: 12,
    loading: false,
    error: null,
    filters: {
      category: null,
      tag: null,
      search: '',
      sort: 'newest'
    }
  }),

  actions: {
    async fetchRecipes(reset = false) {
      if (reset) {
        this.page = 1
        this.recipes = []
      }
      this.loading = true
      this.error = null
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
          sort: this.filters.sort
        }
        if (this.filters.category) params.category = this.filters.category
        if (this.filters.tag) params.tag = this.filters.tag
        if (this.filters.search) params.search = this.filters.search

        const result = await api.getRecipes(params)
        this.recipes = result.data || []
        this.total = result.total || 0
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async fetchRecipe(slug) {
      this.loading = true
      this.error = null
      try {
        this.currentRecipe = await api.getRecipe(slug)
      } catch (e) {
        this.error = e.message
        this.currentRecipe = null
      } finally {
        this.loading = false
      }
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.fetchRecipes(true)
    },

    clearFilters() {
      this.filters = { category: null, tag: null, search: '', sort: 'newest' }
      this.fetchRecipes(true)
    }
  }
})
