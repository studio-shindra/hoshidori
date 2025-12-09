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
import Settings from '@/pages/Settings.vue'

const routes = [
  { path: '/', redirect: '/logs' },
  { path: '/logs', name: 'logs', component: LogsPage },
  { path: '/logs/new', name: 'log-new', component: LogNewPage },
  {
    path: '/logs/:id/detail',
    name: 'log-detail',
    component: LogsDetailPage,
    props: true,
  },
  {
    path: '/logs/:id/edit',
    name: 'log-edit',
    component: LogEditPage,
    props: true,
  },
  { path: '/works', name: 'works', component: WorksList },
  {
    path: '/works/:id/detail',
    name: 'work-detail',
    component: WorksDetailPage,
    props: true,
  },
  { path: '/works/new', name: 'work-new', component: WorksNewPage },
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
  { path: '/works-test', component: WorksTestPage },
  { path: '/contact', component: ContactPage },
  { path: '/about-contents', component: AboutContentsPage },
  { path: '/settings', component: Settings }, // ゲストでもアクセス可能
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// グローバルガード：必須ページのみログインを要求。それ以外はゲスト利用を許可。
router.beforeEach((to, _from, next) => {
  // 認証状態を待たずに通すことでゲスト利用を許可
  if (!authReady.value) {
    return next()
  }

  if (to.meta.requiresAuth && !currentUser.value) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if ((to.name === 'login' || to.name === 'signup') && currentUser.value) {
    // ログイン済みでログイン/サインアップへ来た場合はトップへ
    return next({ name: 'logs' })
  }

  next()
})

export default router