<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useRecipesStore } from '@/stores/recipes'
import CategoryBar from '@/components/category/CategoryBar.vue'
import RecipeCard from '@/components/recipe/RecipeCard.vue'

const route = useRoute()
const recipesStore = useRecipesStore()

onMounted(() => {
  recipesStore.setFilter('category', route.params.slug)
})

watch(() => route.params.slug, (newSlug) => {
  recipesStore.setFilter('category', newSlug)
})
</script>

<template>
  <div>
    <CategoryBar />
    <div class="recipe-grid">
      <RecipeCard
        v-for="recipe in recipesStore.recipes"
        :key="recipe.id"
        :recipe="recipe"
      />
    </div>
    <div v-if="recipesStore.recipes.length === 0 && !recipesStore.loading" class="empty-state">
      <p>{{ $t('recipe.noRecipes') }}</p>
    </div>
  </div>
</template>

<style scoped>
.recipe-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}
</style>
