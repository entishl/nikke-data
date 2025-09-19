import { createRouter, createWebHistory } from 'vue-router';
import UnionManagementView from '../views/UnionManagementView.vue';
import PlayerDataHubView from '../views/PlayerDataHubView.vue';
import { useAuthStore } from '@/stores/authStore';

const routes = [
  {
    path: '/',
    redirect: '/unions',
  },
  {
    path: '/login',
    name: 'Login',
    // Component will be created in a future task
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
  },
  {
    path: '/unions',
    name: 'UnionManagement',
    component: UnionManagementView,
    meta: { requiresAuth: true },
  },
  {
    path: '/players',
    name: 'PlayerDataHub',
    component: PlayerDataHubView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
