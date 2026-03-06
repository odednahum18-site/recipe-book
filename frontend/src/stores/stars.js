import { defineStore } from 'pinia'
import api from '@/api'

function getVisitorId() {
  let id = localStorage.getItem('recipe-book-visitor-id')
  if (!id) {
    id = 'v_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
    localStorage.setItem('recipe-book-visitor-id', id)
  }
  return id
}

export const useStarsStore = defineStore('stars', {
  state: () => ({
    starredRecipes: new Set(),
    visitorId: getVisitorId()
  }),

  actions: {
    async toggleStar(recipeId) {
      const isStarred = this.starredRecipes.has(recipeId)
      try {
        if (isStarred) {
          await api.unstarRecipe(recipeId, this.visitorId)
          this.starredRecipes.delete(recipeId)
        } else {
          await api.starRecipe(recipeId, this.visitorId)
          this.starredRecipes.add(recipeId)
        }
        return true
      } catch (e) {
        return false
      }
    },

    async checkStarred(recipeId) {
      try {
        const result = await api.checkStarred(recipeId, this.visitorId)
        if (result.starred) {
          this.starredRecipes.add(recipeId)
        } else {
          this.starredRecipes.delete(recipeId)
        }
      } catch (e) {
        // ignore
      }
    },

    isStarred(recipeId) {
      return this.starredRecipes.has(recipeId)
    }
  }
})
