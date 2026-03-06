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

    <div v-if="recipesStore.loading" class="loading-state">
      <div class="skeleton-grid">
        <el-skeleton v-for="n in 6" :key="n" animated>
          <template #template>
            <el-skeleton-item variant="image" style="height: 180px; border-radius: 12px 12px 0 0" />
            <div style="padding: 14px">
              <el-skeleton-item variant="text" style="width: 60%; margin-bottom: 8px" />
              <el-skeleton-item variant="text" style="width: 40%" />
            </div>
          </template>
        </el-skeleton>
      </div>
    </div>

    <div v-else-if="recipesStore.recipes.length === 0" class="empty-state">
      <div class="empty-icon">&#128218;</div>
      <p>{{ $t('recipe.noRecipes') }}</p>
    </div>

    <div v-else class="recipe-grid">
      <RecipeCard
        v-for="recipe in recipesStore.recipes"
        :key="recipe.id"
        :recipe="recipe"
      />
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

.loading-state,
.empty-state {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 40px;
  text-align: center;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}
</style>
