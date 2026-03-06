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

    <div v-if="recipesStore.loading" class="skeleton-grid">
      <el-skeleton v-for="n in 6" :key="n" animated>
        <template #template>
          <el-skeleton-item variant="image" class="skeleton-card-image" />
          <div class="skeleton-card-body">
            <el-skeleton-item variant="text" class="skeleton-card-title" />
            <el-skeleton-item variant="text" class="skeleton-card-subtitle" />
          </div>
        </template>
      </el-skeleton>
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
.empty-state {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 40px;
  text-align: center;
}
</style>
