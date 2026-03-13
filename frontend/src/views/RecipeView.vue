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
const portionMultiplier = ref(1)

const baseServings = computed(() => recipe.value?.servings || null)
const currentServings = computed(() => baseServings.value ? Math.round(baseServings.value * portionMultiplier.value) : null)

function adjustPortions(delta) {
  const newVal = portionMultiplier.value + delta
  if (newVal >= 0.25 && newVal <= 10) {
    portionMultiplier.value = Math.round(newVal * 4) / 4 // snap to 0.25 increments
  }
}

function scaleAmount(amount) {
  if (!amount || portionMultiplier.value === 1) return amount
  const num = parseFloat(amount)
  if (isNaN(num)) return amount
  const scaled = num * portionMultiplier.value
  // Show clean fractions
  if (scaled === Math.floor(scaled)) return String(scaled)
  if (Math.abs(scaled - Math.round(scaled * 4) / 4) < 0.01) {
    const rounded = Math.round(scaled * 4) / 4
    if (rounded === Math.floor(rounded)) return String(rounded)
    const whole = Math.floor(rounded)
    const frac = rounded - whole
    const fracs = { 0.25: '¼', 0.5: '½', 0.75: '¾' }
    const fracStr = fracs[frac] || frac.toFixed(2)
    return whole > 0 ? `${whole}${fracStr}` : fracStr
  }
  return scaled % 1 === 0 ? String(scaled) : scaled.toFixed(1)
}

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

// Focus Mode
const focusMode = ref(false)
const focusStep = ref(0)

const parsedSteps = computed(() => {
  const html = steps.value
  if (!html) return []
  // Try to extract from <ol>/<li> elements
  const liMatch = html.match(/<li[^>]*>([\s\S]*?)<\/li>/gi)
  if (liMatch && liMatch.length > 1) {
    return liMatch.map(li => li.replace(/<\/?li[^>]*>/gi, '').trim())
  }
  // Fall back to splitting by <p> tags
  const pMatch = html.match(/<p[^>]*>([\s\S]*?)<\/p>/gi)
  if (pMatch && pMatch.length > 1) {
    return pMatch.map(p => p.replace(/<\/?p[^>]*>/gi, '').trim()).filter(Boolean)
  }
  // Fall back to splitting by <br> or newlines
  const parts = html.split(/<br\s*\/?>/gi).map(s => s.trim()).filter(Boolean)
  return parts.length > 1 ? parts : [html]
})

function enterFocusMode() {
  focusStep.value = 0
  focusMode.value = true
}

function exitFocusMode() {
  focusMode.value = false
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
      <div v-if="recipe.prep_time || recipe.difficulty" class="recipe-detail-meta">
        <span v-if="recipe.prep_time" class="detail-meta-badge"><span aria-hidden="true">&#9200;</span> {{ recipe.prep_time }}</span>
        <span v-if="recipe.difficulty" class="detail-meta-badge">{{ $t(`recipe.difficulty.${recipe.difficulty}`) }}</span>
      </div>

      <!-- Actions row -->
      <div class="actions-row no-print">
        <div class="star-section">
          <button class="star-btn" :class="{ active: isStarred }" @click="toggleStar" :aria-label="isStarred ? $t('recipe.unstar') : $t('recipe.star')" :aria-pressed="isStarred">
            <span aria-hidden="true">{{ isStarred ? '&#9733;' : '&#9734;' }}</span>
          </button>
          <span class="star-count" aria-hidden="true">{{ recipe.star_count || 0 }}</span>
        </div>
        <div class="share-buttons">
          <button class="icon-btn whatsapp" @click="shareWhatsApp" :aria-label="$t('share.whatsapp')">
            <span aria-hidden="true">&#128172;</span> {{ $t('share.whatsapp') }}
          </button>
          <button class="icon-btn" @click="window.print()" :aria-label="$t('share.print')">
            <span aria-hidden="true">&#128424;</span> {{ $t('share.print') }}
          </button>
        </div>
      </div>

      <!-- Ingredients -->
      <div class="ingredients-header">
        <h2 class="section-title"><span aria-hidden="true">&#129379;</span> {{ $t('recipe.ingredients') }}</h2>
        <div v-if="baseServings" class="portion-calculator no-print">
          <button class="portion-btn" @click="adjustPortions(-0.25)" :disabled="portionMultiplier <= 0.25" :aria-label="$t('recipe.decreasePortions')">&#8722;</button>
          <span class="portion-value">{{ currentServings }} {{ $t('recipe.servings') }}</span>
          <button class="portion-btn" @click="adjustPortions(0.25)" :disabled="portionMultiplier >= 10" :aria-label="$t('recipe.increasePortions')">&#43;</button>
        </div>
      </div>
      <ul class="ingredients-list" role="list">
        <li v-for="(ing, idx) in ingredients" :key="idx" role="checkbox" :aria-checked="checkedIngredients.has(idx)" tabindex="0" @click="toggleIngredient(idx)" @keydown.enter.prevent="toggleIngredient(idx)" @keydown.space.prevent="toggleIngredient(idx)">
          <div class="ingredient-check" :class="{ checked: checkedIngredients.has(idx) }" aria-hidden="true">
            <span v-if="checkedIngredients.has(idx)">&#10003;</span>
          </div>
          <span :class="{ 'checked-text': checkedIngredients.has(idx) }">
            {{ scaleAmount(ing.amount) }} {{ typeof ing.unit === 'object' ? (ing.unit?.[locale] || ing.unit?.en || '') : (ing.unit || '') }} {{ ing.text?.[locale] || ing.text?.en || '' }}
          </span>
        </li>
      </ul>

      <!-- Steps -->
      <div class="steps-header">
        <h2 class="section-title"><span aria-hidden="true">&#128203;</span> {{ $t('recipe.steps') }}</h2>
        <button v-if="parsedSteps.length > 1" class="icon-btn no-print" @click="enterFocusMode" :aria-label="$t('recipe.focusMode')">
          <span aria-hidden="true">&#127859;</span> {{ $t('recipe.focusMode') }}
        </button>
      </div>
      <div class="steps-content" v-html="steps"></div>
    </div>

    <!-- Focus Mode Overlay -->
    <Teleport to="body">
      <div v-if="focusMode" class="focus-overlay" @keydown.escape="exitFocusMode">
        <div class="focus-container">
          <div class="focus-header">
            <span class="focus-step-counter">{{ focusStep + 1 }} / {{ parsedSteps.length }}</span>
            <button class="focus-close" @click="exitFocusMode" :aria-label="$t('common.close')">&#10005;</button>
          </div>
          <div class="focus-progress">
            <div class="focus-progress-bar" :style="{ width: `${((focusStep + 1) / parsedSteps.length) * 100}%` }"></div>
          </div>
          <div class="focus-step-content" v-html="parsedSteps[focusStep]"></div>
          <div class="focus-nav">
            <button class="focus-nav-btn" :disabled="focusStep <= 0" @click="focusStep--">&#8592; {{ $t('recipe.prevStep') }}</button>
            <button v-if="focusStep < parsedSteps.length - 1" class="focus-nav-btn primary" @click="focusStep++">{{ $t('recipe.nextStep') }} &#8594;</button>
            <button v-else class="focus-nav-btn primary" @click="exitFocusMode">&#10003; {{ $t('recipe.done') }}</button>
          </div>
        </div>
      </div>
    </Teleport>
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

.recipe-detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 50px;
  background: var(--category-bg);
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--border);
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

.ingredients-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.ingredients-header .section-title {
  margin-bottom: 0;
}

.portion-calculator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.portion-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--category-bg);
  color: var(--text);
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  font-family: inherit;
  line-height: 1;
}

.portion-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.portion-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.portion-value {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  min-width: 80px;
  text-align: center;
}

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

.steps-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.steps-header .section-title {
  margin-bottom: 0;
}

/* Focus Mode */
.focus-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.focus-container {
  max-width: 600px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.focus-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.focus-step-counter {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.focus-close {
  background: none;
  border: none;
  font-size: 1.3rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.focus-close:hover {
  color: var(--text);
}

.focus-progress {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.focus-progress-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.focus-step-content {
  font-size: 1.4rem;
  line-height: 1.8;
  color: var(--text);
  text-align: center;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.focus-nav {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.focus-nav-btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  font-family: inherit;
}

.focus-nav-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.focus-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.focus-nav-btn.primary {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.focus-nav-btn.primary:hover {
  background: var(--accent-dark);
  border-color: var(--accent-dark);
  color: white;
}

@media (max-width: 768px) {
  .recipe-body { padding: 16px; }
  .recipe-body h1 { font-size: 1.4rem; }
  .share-buttons { flex-direction: column; }

  .focus-step-content {
    font-size: 1.2rem;
  }
}
</style>
