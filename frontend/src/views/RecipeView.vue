<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useRecipesStore } from '@/stores/recipes'
import { useLocaleStore } from '@/stores/locale'
import { useCategoriesStore } from '@/stores/categories'
import { useStarsStore } from '@/stores/stars'
import api from '@/api'

const route = useRoute()
const { t } = useI18n()
const recipesStore = useRecipesStore()
const localeStore = useLocaleStore()
const categoriesStore = useCategoriesStore()
const starsStore = useStarsStore()
const checkedIngredients = ref(new Set())
const allTags = ref([])

onMounted(async () => {
  await recipesStore.fetchRecipe(route.params.slug)
  if (recipesStore.currentRecipe) {
    starsStore.checkStarred(recipesStore.currentRecipe.id)
  }
  try {
    allTags.value = await api.getTags()
  } catch (e) {
    // Tags are non-critical
  }
})

const recipe = computed(() => recipesStore.currentRecipe)
const locale = computed(() => localeStore.locale)

const name = computed(() => recipe.value?.name?.[locale.value] || recipe.value?.name?.en || '')
const recipeOf = computed(() => recipe.value?.recipe_of?.[locale.value] || recipe.value?.recipe_of?.en || '')
const steps = computed(() => recipe.value?.steps?.[locale.value] || recipe.value?.steps?.en || '')
const ingredients = computed(() => recipe.value?.ingredients || [])

const categoryNames = computed(() => {
  if (!recipe.value) return []
  const ids = recipe.value.category_ids || (recipe.value.category_id ? [recipe.value.category_id] : [])
  return ids.map(id => {
    const cat = categoriesStore.getCategoryById(id)
    return cat?.name?.[locale.value] || cat?.name?.en || ''
  }).filter(Boolean)
})

const recipeTags = computed(() => {
  if (!recipe.value?.tags?.length) return []
  return recipe.value.tags.map(slug => {
    const tag = allTags.value.find(t => t.slug === slug)
    return tag?.name?.[locale.value] || tag?.name?.en || slug
  })
})

const isStarred = computed(() => recipe.value && starsStore.isStarred(recipe.value.id))

function toggleIngredient(index) {
  if (checkedIngredients.value.has(index)) {
    checkedIngredients.value.delete(index)
  } else {
    checkedIngredients.value.add(index)
  }
}

async function toggleStar() {
  if (recipe.value) {
    const success = await starsStore.toggleStar(recipe.value.id)
    if (success) {
      // Refresh recipe to get updated star_count
      recipesStore.fetchRecipe(route.params.slug)
    }
  }
}

function shareWhatsApp() {
  const text = `${t('share.shareText')} ${name.value} - ${window.location.href}`
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank')
}
</script>

<template>
  <div v-if="recipesStore.loading" class="recipe-detail loading-state">
    <el-skeleton :rows="8" animated />
  </div>

  <div v-else-if="!recipe" class="recipe-detail empty-state">
    <p>Recipe not found</p>
  </div>

  <div v-else class="recipe-detail">
    <!-- Hero image -->
    <div class="recipe-hero">
      <img
        v-if="recipe.images && recipe.images.length"
        :src="recipe.images[0].url"
        :alt="name"
      />
      <div v-else class="recipe-hero-placeholder">&#127859;</div>
    </div>

    <div class="recipe-body">
      <div class="recipe-badges">
        <span v-for="catName in categoryNames" :key="catName" class="recipe-category-badge">{{ catName }}</span>
        <span v-for="tagName in recipeTags" :key="tagName" class="recipe-tag-badge">{{ tagName }}</span>
      </div>
      <h1>{{ name }}</h1>
      <p v-if="recipeOf" class="recipe-of">{{ $t('recipe.recipeOf') }} {{ recipeOf }}</p>

      <!-- Actions row -->
      <div class="actions-row no-print">
        <div class="star-section">
          <button class="star-btn" :class="{ active: isStarred }" @click="toggleStar">
            {{ isStarred ? '&#9733;' : '&#9734;' }}
          </button>
          <span class="star-count">{{ recipe.star_count || 0 }}</span>
        </div>
        <div class="share-buttons">
          <button class="icon-btn whatsapp" @click="shareWhatsApp">
            &#128172; {{ $t('share.whatsapp') }}
          </button>
          <button class="icon-btn" @click="window.print()">
            &#128424; {{ $t('share.print') }}
          </button>
        </div>
      </div>

      <!-- Ingredients -->
      <h2 class="section-title">&#129379; {{ $t('recipe.ingredients') }}</h2>
      <ul class="ingredients-list">
        <li v-for="(ing, idx) in ingredients" :key="idx" @click="toggleIngredient(idx)">
          <div class="ingredient-check" :class="{ checked: checkedIngredients.has(idx) }">
            <span v-if="checkedIngredients.has(idx)">&#10003;</span>
          </div>
          <span :class="{ 'checked-text': checkedIngredients.has(idx) }">
            {{ ing.amount }} {{ typeof ing.unit === 'object' ? (ing.unit?.[locale] || ing.unit?.en || '') : (ing.unit || '') }} {{ ing.text?.[locale] || ing.text?.en || '' }}
          </span>
        </li>
      </ul>

      <!-- Steps -->
      <h2 class="section-title">&#128203; {{ $t('recipe.steps') }}</h2>
      <div class="steps-content" v-html="steps"></div>
    </div>
  </div>
</template>

<style scoped>
.recipe-detail {
  max-width: 720px;
  margin: 0 auto;
}

.loading-state, .empty-state {
  padding: 40px 20px;
  text-align: center;
}

.recipe-hero {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: linear-gradient(135deg, var(--category-bg), var(--border));
}

.recipe-hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-hero-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 5rem;
}

.recipe-body {
  padding: 24px;
}

.recipe-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.recipe-category-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 50px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 600;
}

.recipe-tag-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 50px;
  background: var(--category-bg);
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid var(--border);
}

.recipe-of {
  font-size: 1rem;
  color: var(--text-secondary);
  font-style: italic;
  margin-bottom: 16px;
}

.recipe-body h1 {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 12px;
}

.star-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-btn {
  font-size: 1.8rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--star-empty);
  transition: transform 0.15s ease, color 0.15s ease;
  padding: 0;
  line-height: 1;
}

.star-btn.active { color: var(--star); }
.star-btn:hover { transform: scale(1.2); }

.star-count {
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 600;
}

.share-buttons {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: var(--category-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all var(--transition);
  font-family: inherit;
}

.icon-btn:hover { border-color: var(--accent); color: var(--accent); }
.icon-btn.whatsapp:hover { border-color: #25d366; color: #25d366; }

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ingredients-list {
  list-style: none;
  margin-bottom: 28px;
}

.ingredients-list li {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.ingredients-list li:last-child { border-bottom: none; }

.ingredient-check {
  width: 22px;
  height: 22px;
  border: 2px solid var(--border);
  border-radius: 6px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  font-size: 0.75rem;
}

.ingredient-check.checked {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.checked-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.steps-content {
  font-size: 0.95rem;
  line-height: 1.8;
  color: var(--text);
}

.steps-content :deep(p) {
  margin-bottom: 12px;
}

.steps-content :deep(ol), .steps-content :deep(ul) {
  padding-inline-start: 24px;
  margin-bottom: 12px;
}

@media (max-width: 768px) {
  .recipe-body { padding: 16px; }
  .recipe-body h1 { font-size: 1.4rem; }
  .share-buttons { flex-direction: column; }
}
</style>
