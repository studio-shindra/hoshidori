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
      path: '/works/:slug/poster',
      name: 'poster-upload',
      component: () => import('../views/PosterUploadView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/performances/new',
      name: 'performance-create',
      component: () => import('../views/PerformanceCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/logs',
      name: 'logs',
      component: () => import('../views/ViewingLogsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/logs/new',
      name: 'log-create',
      component: () => import('../views/ViewingLogCreateView.vue'),
      meta: { requiresAuth: true },
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
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mock',
      name: 'mock',
      component: () => import('../views/MockView.vue'),
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
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      return { name: 'login', query: { next: to.fullPath } }
    }
  }
})

export default router
