<script setup>
import { ref, onMounted } from 'vue'
import { useRecipesStore } from '@/stores/recipes'
import CategoryBar from '@/components/category/CategoryBar.vue'
import RecipeCard from '@/components/recipe/RecipeCard.vue'

const recipesStore = useRecipesStore()
const searchText = ref('')
let searchTimeout = null

onMounted(() => {
  recipesStore.fetchRecipes(true)
})

function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    recipesStore.setFilter('search', searchText.value)
  }, 400)
}
</script>

<template>
  <div>
    <section class="hero">
      <h1>{{ $t('app.title') }}</h1>
      <p>{{ $t('app.subtitle') }}</p>
      <div class="search-container">
        <span class="search-icon">&#128269;</span>
        <input
          v-model="searchText"
          type="text"
          class="search-input"
          :placeholder="$t('search.placeholder')"
          @input="onSearch"
        />
      </div>
    </section>

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
      <div class="empty-icon">&#127859;</div>
      <p>{{ $t('recipe.noRecipes') }}</p>
    </div>

    <div v-else class="recipe-grid">
      <RecipeCard
        v-for="(recipe, index) in recipesStore.recipes"
        :key="recipe.id"
        :recipe="recipe"
        class="fade-in-up"
        :style="{ animationDelay: `${index * 0.05}s` }"
      />
    </div>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 48px 20px 32px;
  max-width: 600px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 2.4rem;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.hero p {
  color: var(--text-secondary);
  font-size: 1.05rem;
  margin-bottom: 24px;
}

.search-container {
  max-width: 480px;
  margin: 0 auto;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.95rem;
  outline: none;
  transition: all var(--transition);
  font-family: inherit;
}

[dir="rtl"] .search-input {
  padding: 12px 44px 12px 16px;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 1.1rem;
}

[dir="rtl"] .search-icon {
  left: auto;
  right: 14px;
}

.empty-state {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .hero h1 { font-size: 1.7rem; }
  .hero { padding: 32px 16px 24px; }
}
</style>
