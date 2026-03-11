<script setup>
import { computed } from 'vue'
import { useLocaleStore } from '@/stores/locale'
import { useCategoriesStore } from '@/stores/categories'

const props = defineProps({
  recipe: { type: Object, required: true }
})

const localeStore = useLocaleStore()
const categoriesStore = useCategoriesStore()

const name = computed(() => {
  const n = props.recipe.name
  return n?.[localeStore.locale] || n?.en || n?.he || ''
})

const categoryNames = computed(() => {
  const ids = props.recipe.category_ids || (props.recipe.category_id ? [props.recipe.category_id] : [])
  return ids.map(id => {
    const cat = categoriesStore.getCategoryById(id)
    return cat?.name?.[localeStore.locale] || cat?.name?.en || ''
  }).filter(Boolean)
})

const thumbnail = computed(() => {
  const images = props.recipe.images
  if (images && images.length > 0) {
    return images[0].thumbnail_url || images[0].url
  }
  return null
})
</script>

<template>
  <router-link :to="`/recipe/${recipe.slug}`" class="recipe-card">
    <div class="recipe-image">
      <img v-if="thumbnail" :src="thumbnail" :alt="name" loading="lazy" />
      <div v-else class="recipe-placeholder">&#127859;</div>
    </div>
    <div class="recipe-info">
      <div class="recipe-badges">
        <span v-for="catName in categoryNames" :key="catName" class="recipe-category-badge">{{ catName }}</span>
      </div>
      <div class="recipe-name">{{ name }}</div>
      <div class="recipe-meta">
        <span class="recipe-stars">&#9733; {{ recipe.star_count || 0 }}</span>
      </div>
    </div>
  </router-link>
</template>

<style scoped>
.recipe-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
  transition: all 0.25s ease;
  cursor: pointer;
  display: block;
}

.recipe-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.recipe-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: linear-gradient(135deg, var(--category-bg), var(--border));
}

.recipe-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
}

.recipe-info {
  padding: 16px;
}

.recipe-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.recipe-category-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 50px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 0.75rem;
  font-weight: 600;
}

.recipe-name {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.3;
}

.recipe-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.recipe-stars {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--star);
  font-weight: 600;
}

@media (max-width: 768px) {
  .recipe-info { padding: 12px; }
  .recipe-name { font-size: 0.95rem; }
  .recipe-meta { font-size: 0.78rem; }
}
</style>
