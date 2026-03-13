<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useLocaleStore } from '@/stores/locale'
import { useAuthStore } from '@/stores/auth'
import { useCategoriesStore } from '@/stores/categories'
import AppHeader from '@/components/layout/AppHeader.vue'
import MobileNav from '@/components/layout/MobileNav.vue'

const themeStore = useThemeStore()
const localeStore = useLocaleStore()
const authStore = useAuthStore()
const categoriesStore = useCategoriesStore()

onMounted(() => {
  themeStore.initTheme()
  localeStore.initLocale()
  authStore.initAuth()
  categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="app-container">
    <a href="#main-content" class="skip-link">{{ $t('common.skipToContent') }}</a>
    <AppHeader />
    <main id="main-content" class="app-main" role="main">
      <router-view />
    </main>
    <footer class="app-footer no-print">
      <span>{{ $t('app.footer') }}</span>
    </footer>
    <MobileNav />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding-bottom: 20px;
}

.app-footer {
  text-align: center;
  padding: 32px 20px;
  color: var(--text-muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .app-main {
    padding-bottom: 72px;
  }
}
</style>
