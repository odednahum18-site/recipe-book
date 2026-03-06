<script setup>
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useLocaleStore } from '@/stores/locale'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const themeStore = useThemeStore()
const localeStore = useLocaleStore()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="app-header no-print">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <div class="logo-icon">&#127859;</div>
        <span class="logo-text">{{ $t('app.title') }}</span>
      </router-link>

      <div class="header-actions">
        <button class="toggle-btn" @click="localeStore.toggleLocale()" :title="$t('nav.home')">
          <span>&#127760;</span>
          <span class="label-text">{{ localeStore.isHebrew ? 'HE' : 'EN' }}</span>
        </button>

        <button class="toggle-btn" @click="themeStore.toggleTheme()" title="Toggle theme">
          <span>{{ themeStore.isDark ? '&#9788;' : '&#9790;' }}</span>
        </button>

        <template v-if="authStore.isLoggedIn">
          <button class="toggle-btn desktop-only" @click="router.push('/admin')">
            <span>&#128221;</span>
            <span class="label-text">{{ $t('nav.admin') }}</span>
          </button>
          <button class="toggle-btn desktop-only" @click="handleLogout">
            <span>&#128682;</span>
          </button>
        </template>
        <button v-else class="toggle-btn desktop-only" @click="router.push('/login')">
          <span>&#128274;</span>
          <span class="label-text">{{ $t('auth.login') }}</span>
        </button>
      </div>
    </div>
  </header>
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
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
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
}
</style>
