import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
    { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue') },
    {
      path: '/theaters',
      name: 'theaters',
      component: () => import('../views/TheatersListView.vue'),
    },
    {
      path: '/theaters/:slug',
      name: 'theater-detail',
      component: () => import('../views/TheaterDetailView.vue'),
    },
    { path: '/works', name: 'works', component: () => import('../views/WorksListView.vue') },
    {
      path: '/works/:slug',
      name: 'work-detail',
      component: () => import('../views/WorkDetailView.vue'),
    },
    {
      path: '/works/new',
      name: 'work-create',
      component: () => import('../views/WorkCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/works/:slug/edit',
      name: 'work-edit',
      component: () => import('../views/WorkEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/performances/new',
      name: 'performance-create',
      redirect: { name: 'works' },
    },
    {
      path: '/logs',
      name: 'logs',
      redirect: { name: 'mypage' },
      meta: { requiresAuth: true },
    },
    {
      path: '/logs/new',
      name: 'log-create',
      component: () => import('../views/ViewingLogCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/shops',
      name: 'shops',
      component: () => import('../views/ShopListView.vue'),
    },
    {
      path: '/shops/:slug',
      name: 'shop-detail',
      component: () => import('../views/ShopDetailView.vue'),
    },
    {
      path: '/mypage',
      name: 'mypage',
      component: () => import('../views/MyPageView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mypage/edit',
      name: 'profile-edit',
      component: () => import('../views/ProfileEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/blocked-users',
      name: 'blocked-users',
      component: () => import('../views/BlockedUsersView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true, requiresShop: true },
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue'),
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyView.vue'),
    },
    {
      path: '/guidelines',
      name: 'guidelines',
      component: () => import('../views/GuidelinesView.vue'),
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/ContactView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

let authReady = false

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth || to.meta.requiresShop) {
    const auth = useAuthStore()
    if (!authReady) {
      await auth.fetchMe()
      authReady = true
    }
    if (!auth.isAuthenticated) {
      return { name: 'login', query: { next: to.fullPath } }
    }
    if (to.meta.requiresShop && !auth.isShopUser) {
      return { name: 'mypage' }
    }
  }
})

export default router
