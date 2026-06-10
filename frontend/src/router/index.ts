import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { hideSidebar: true, guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/Register.vue'),
      meta: { hideSidebar: true, guest: true },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/Search.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/papers/:id',
      name: 'paper-detail',
      component: () => import('@/views/PaperDetail.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/collections',
      name: 'collections',
      component: () => import('@/views/Collections.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/collections/:id',
      name: 'collection-detail',
      component: () => import('@/views/CollectionDetail.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/gap-analysis',
      name: 'gap-analysis',
      component: () => import('@/views/GapAnalysis.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/History.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
