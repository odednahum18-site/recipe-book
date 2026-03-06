<script setup>
import { computed } from 'vue'
import { useLocaleStore } from '@/stores/locale'
import { useCategoriesStore } from '@/stores/categories'
import { useRecipesStore } from '@/stores/recipes'

const localeStore = useLocaleStore()
const categoriesStore = useCategoriesStore()
const recipesStore = useRecipesStore()

const activeCategory = computed(() => recipesStore.filters.category)

function selectCategory(slug) {
  recipesStore.setFilter('category', slug === activeCategory.value ? null : slug)
}

function getCategoryName(cat) {
  return cat.name?.[localeStore.locale] || cat.name?.en || ''
}
</script>

<template>
  <div class="categories">
    <div class="categories-inner">
      <button
        class="category-pill"
        :class="{ active: !activeCategory }"
        @click="selectCategory(null)"
      >
        {{ $t('category.all') }}
      </button>
      <button
        v-for="cat in categoriesStore.categories"
        :key="cat.id"
        class="category-pill"
        :class="{ active: activeCategory === cat.slug }"
        @click="selectCategory(cat.slug)"
      >
        {{ getCategoryName(cat) }}
        <span class="category-count">{{ cat.recipe_count }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.categories {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.categories::-webkit-scrollbar { display: none; }

.categories-inner {
  display: flex;
  gap: 8px;
  padding: 8px 0 24px;
  min-width: max-content;
}

.category-pill {
  padding: 8px 18px;
  border-radius: 50px;
  background: var(--category-bg);
  color: var(--text-secondary);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  white-space: nowrap;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
}

.category-pill:hover {
  border-color: var(--border);
  color: var(--text);
}

.category-pill.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.category-count {
  font-size: 0.75rem;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .categories { padding: 0 12px; }
}
</style>
