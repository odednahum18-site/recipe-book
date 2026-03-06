<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
</script>

<template>
  <nav class="mobile-nav no-print">
    <div class="mobile-nav-inner">
      <a class="mobile-nav-item" :class="{ active: route.path === '/' }" @click="router.push('/')">
        <span>&#127968;</span>
        <span>{{ $t('nav.home') }}</span>
      </a>
      <a class="mobile-nav-item" :class="{ active: route.path.startsWith('/category') }">
        <span>&#128218;</span>
        <span>{{ $t('nav.categories') }}</span>
      </a>
      <a class="mobile-nav-item">
        <span>&#11088;</span>
        <span>{{ $t('nav.favorites') }}</span>
      </a>
      <a
        class="mobile-nav-item"
        :class="{ active: route.path.startsWith('/admin') || route.path === '/login' }"
        @click="router.push(authStore.isLoggedIn ? '/admin' : '/login')"
      >
        <span>&#128100;</span>
        <span>{{ $t('nav.admin') }}</span>
      </a>
    </div>
  </nav>
</template>

<style scoped>
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-header);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--border);
  z-index: 100;
  padding: 6px 0 calc(6px + env(safe-area-inset-bottom));
}

.mobile-nav-inner {
  display: flex;
  justify-content: space-around;
  max-width: 400px;
  margin: 0 auto;
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 0.7rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  transition: color var(--transition);
}

.mobile-nav-item.active {
  color: var(--accent);
}

.mobile-nav-item span:first-child {
  font-size: 1.3rem;
}

@media (max-width: 768px) {
  .mobile-nav { display: block; }
}
</style>
