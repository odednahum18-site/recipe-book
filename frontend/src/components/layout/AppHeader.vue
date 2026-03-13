<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useLocaleStore } from '@/stores/locale'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const themeStore = useThemeStore()
const localeStore = useLocaleStore()
const authStore = useAuthStore()

const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const searchExpanded = ref(false)
let searchTimeout = null

function handleLogout() {
  authStore.logout()
  router.push('/')
}

function onSearchInput() {
  clearTimeout(searchTimeout)
  const q = searchQuery.value.trim()
  if (!q) {
    searchResults.value = []
    showResults.value = false
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const data = await api.searchRecipes(q)
      searchResults.value = data.data || []
      showResults.value = searchResults.value.length > 0
    } catch {
      searchResults.value = []
    }
  }, 300)
}

function selectResult(recipe) {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
  searchExpanded.value = false
  router.push(`/recipe/${recipe.slug}`)
}

function closeSearch() {
  showResults.value = false
  searchExpanded.value = false
  searchQuery.value = ''
  searchResults.value = []
}

function getRecipeName(recipe) {
  return recipe.name?.[localeStore.locale] || recipe.name?.en || ''
}
</script>

<template>
  <header class="app-header no-print">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <div class="logo-icon">&#127859;</div>
        <span class="logo-text">{{ $t('app.title') }}</span>
      </router-link>

      <div class="header-search" :class="{ expanded: searchExpanded }">
        <div class="search-wrapper">
          <span class="search-icon" aria-hidden="true">&#128269;</span>
          <input
            v-model="searchQuery"
            type="text"
            class="header-search-input"
            :placeholder="$t('search.placeholder')"
            :aria-label="$t('search.placeholder')"
            @input="onSearchInput"
            @focus="searchExpanded = true; if (searchResults.length) showResults = true"
            @keydown.escape="closeSearch"
          />
          <button v-if="searchExpanded" class="search-close" @click="closeSearch" :aria-label="$t('common.close')">&#10005;</button>
        </div>
        <div v-if="showResults" class="search-dropdown">
          <button
            v-for="recipe in searchResults"
            :key="recipe.id"
            class="search-result-item"
            @mousedown.prevent="selectResult(recipe)"
          >
            <img v-if="recipe.images?.length" :src="recipe.images[0].thumbnail_url || recipe.images[0].url" :alt="getRecipeName(recipe)" class="search-result-thumb" />
            <span v-else class="search-result-placeholder" aria-hidden="true">&#127859;</span>
            <span class="search-result-name">{{ getRecipeName(recipe) }}</span>
          </button>
        </div>
      </div>

      <div class="header-actions">
        <button class="toggle-btn search-toggle-mobile" @click="searchExpanded = !searchExpanded" :aria-label="$t('search.placeholder')">
          <span aria-hidden="true">&#128269;</span>
        </button>

        <button class="toggle-btn" @click="localeStore.toggleLocale()" :aria-label="$t('nav.toggleLanguage')" :title="$t('nav.toggleLanguage')">
          <span aria-hidden="true">&#127760;</span>
          <span class="label-text">{{ localeStore.isHebrew ? 'HE' : 'EN' }}</span>
        </button>

        <button class="toggle-btn" @click="themeStore.toggleTheme()" :aria-label="$t('nav.toggleTheme')" :title="$t('nav.toggleTheme')">
          <span aria-hidden="true">{{ themeStore.isDark ? '&#9788;' : '&#9790;' }}</span>
        </button>

        <template v-if="authStore.isLoggedIn">
          <button class="toggle-btn desktop-only" @click="router.push('/admin')" :aria-label="$t('nav.admin')">
            <span aria-hidden="true">&#128221;</span>
            <span class="label-text">{{ $t('nav.admin') }}</span>
          </button>
          <button class="toggle-btn desktop-only" @click="handleLogout" :aria-label="$t('auth.logout')">
            <span aria-hidden="true">&#128682;</span>
          </button>
        </template>
        <button v-else class="toggle-btn desktop-only" @click="router.push('/login')" :aria-label="$t('auth.login')">
          <span aria-hidden="true">&#128274;</span>
          <span class="label-text">{{ $t('auth.login') }}</span>
        </button>
      </div>
    </div>
  </header>
  <!-- Backdrop for closing search on mobile -->
  <div v-if="searchExpanded" class="search-backdrop" @click="closeSearch"></div>
</template>

<style scoped>
.app-header {
  background: var(--bg-header);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background var(--transition), border-color var(--transition);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  flex-shrink: 0;
}

.logo-icon {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: white;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3);
}

/* Search */
.header-search {
  flex: 1;
  max-width: 400px;
  position: relative;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: var(--text-muted);
  pointer-events: none;
}

[dir="rtl"] .search-icon {
  left: auto;
  right: 12px;
}

.header-search-input {
  width: 100%;
  padding: 8px 32px 8px 36px;
  border: 1px solid var(--border);
  border-radius: 50px;
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.85rem;
  outline: none;
  transition: all var(--transition);
  font-family: inherit;
}

[dir="rtl"] .header-search-input {
  padding: 8px 36px 8px 32px;
}

.header-search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
}

.search-close {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 4px;
  display: none;
}

[dir="rtl"] .search-close {
  right: auto;
  left: 8px;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  z-index: 200;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  width: 100%;
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
  font-size: 0.88rem;
  font-family: inherit;
  text-align: start;
  transition: background var(--transition);
}

.search-result-item:hover {
  background: var(--category-bg);
}

.search-result-thumb {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.search-result-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: var(--category-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.search-result-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-toggle-mobile {
  display: none !important;
}

.search-backdrop {
  display: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.toggle-btn {
  background: var(--category-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 7px 14px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text);
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
}

.toggle-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.label-text {
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .header-inner { padding: 0 12px; }
  .logo-text { display: none; }
  .desktop-only { display: none !important; }
  .label-text { display: none; }

  .header-search {
    display: none;
  }

  .header-search.expanded {
    display: block;
    position: fixed;
    top: 8px;
    left: 12px;
    right: 12px;
    max-width: none;
    z-index: 150;
  }

  .search-close {
    display: block;
  }

  .search-toggle-mobile {
    display: flex !important;
  }

  .search-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: 99;
  }
}
</style>
