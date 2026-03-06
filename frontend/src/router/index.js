import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/recipe/:slug',
    name: 'Recipe',
    component: () => import('@/views/RecipeView.vue')
  },
  {
    path: '/category/:slug',
    name: 'Category',
    component: () => import('@/views/CategoryView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/recipe/new',
    name: 'NewRecipe',
    component: () => import('@/views/RecipeEditorView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/recipe/:id/edit',
    name: 'EditRecipe',
    component: () => import('@/views/RecipeEditorView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/invite',
    name: 'Invite',
    component: () => import('@/views/InviteView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
