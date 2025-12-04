// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import LogsPage from '@/pages/LogsPage.vue'
import LogNewPage from '@/pages/LogNewPage.vue'
import LogEditPage from '@/pages/LogEditPage.vue'
import LogsDetailPage from '@/pages/LogsDetailPage.vue'
import WorksList from '@/pages/WorksList.vue'
import WorksDetailPage from '@/pages/WorksDetailPage.vue'
import WorksNewPage from '@/pages/WorksNewPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import SignUpPage from '@/pages/SignUpPage.vue'
import LoadingTest from '@/pages/LoadingTest.vue'
import { currentUser, authReady } from '@/authState'
import WorksTestPage from '@/pages/WorksTestPage.vue'
import ContactPage from '@/pages/ContactPage.vue'
import AboutContentsPage from '@/pages/AboutContentsPage.vue'

const routes = [
  { path: '/', redirect: '/logs' },
  { path: '/logs', name: 'logs', component: LogsPage, meta: { requiresAuth: true } },
  { path: '/logs/new', name: 'log-new', component: LogNewPage, meta: { requiresAuth: true } },
  {
    path: '/logs/:id/detail',
    name: 'log-detail',
    component: LogsDetailPage,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/logs/:id/edit',
    name: 'log-edit',
    component: LogEditPage,
    props: true,
    meta: { requiresAuth: true },
  },
  { path: '/works', name: 'works', component: WorksList, meta: { requiresAuth: true } },
  {
    path: '/works/:id/detail',
    name: 'work-detail',
    component: WorksDetailPage,
    props: true,
    meta: { requiresAuth: true },
  },
  { path: '/works/new', name: 'work-new', component: WorksNewPage, meta: { requiresAuth: true } },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignUpPage,
  },
  { path: '/loading-test', name: 'loading-test', component: LoadingTest },
  { path: '/works-test', component: WorksTestPage, meta: { requiresAuth: true } },
  { path: '/contact', component: ContactPage },
  { path: '/about-contents', component: AboutContentsPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// グローバルガード：ログイン必須ページは currentUser が必要
router.beforeEach((to, _from, next) => {
  if (!authReady.value) {
    // initAuth が終わってない間は一旦待つ
    return next(false)
  }

  if (to.meta.requiresAuth && !currentUser.value) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.name === 'login' && currentUser.value) {
    // ログイン済みで /login に来たら /logs に飛ばす
    return next({ name: 'logs' })
  }

  next()
})

export default router