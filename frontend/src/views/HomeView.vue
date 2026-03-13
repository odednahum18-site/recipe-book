<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRecipesStore } from '@/stores/recipes'
import { useLocaleStore } from '@/stores/locale'
import CategoryBar from '@/components/category/CategoryBar.vue'
import RecipeCard from '@/components/recipe/RecipeCard.vue'
import api from '@/api'

const recipesStore = useRecipesStore()
const localeStore = useLocaleStore()
const searchText = ref('')
const tags = ref([])
let searchTimeout = null

const activeTag = computed(() => recipesStore.filters.tag)

onMounted(async () => {
  recipesStore.fetchRecipes(true)
  try {
    tags.value = await api.getTags()
  } catch (e) {
    // Tags are non-critical
  }
})

function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    recipesStore.setFilter('search', searchText.value)
  }, 400)
}

function selectTag(slug) {
  recipesStore.setFilter('tag', slug === activeTag.value ? null : slug)
}

function getTagName(tag) {
  return tag.name?.[localeStore.locale] || tag.name?.en || ''
}
</script>

<template>
  <div>
    <section class="hero">
      <h1>{{ $t('app.title') }}</h1>
      <p>{{ $t('app.subtitle') }}</p>
      <div class="search-container">
        <span class="search-icon" aria-hidden="true">&#128269;</span>
        <input
          v-model="searchText"
          type="text"
          class="search-input"
          :placeholder="$t('search.placeholder')"
          :aria-label="$t('search.placeholder')"
          @input="onSearch"
        />
      </div>
    </section>

    <CategoryBar />

    <!-- Tag filter pills -->
    <div v-if="tags.length" class="tag-bar" role="group" :aria-label="$t('tags.title')">
      <div class="tag-bar-inner">
        <span class="tag-label" aria-hidden="true">{{ $t('tags.title') }}:</span>
        <button
          class="tag-pill"
          :class="{ active: !activeTag }"
          :aria-pressed="!activeTag"
          @click="recipesStore.setFilter('tag', null)"
        >
          {{ $t('tags.all') }}
        </button>
        <button
          v-for="tag in tags"
          :key="tag.slug"
          class="tag-pill"
          :class="{ active: activeTag === tag.slug }"
          :aria-pressed="activeTag === tag.slug"
          @click="selectTag(tag.slug)"
        >
          {{ getTagName(tag) }}
        </button>
      </div>
    </div>

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

.tag-bar {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.tag-bar-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 16px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.tag-pill {
  padding: 5px 14px;
  border-radius: 50px;
  background: var(--category-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border);
  white-space: nowrap;
  transition: all var(--transition);
  font-family: inherit;
}

.tag-pill:hover {
  border-color: var(--accent);
  color: var(--text);
}

.tag-pill.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
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
  .tag-bar { padding: 0 12px; }
}
</style>
