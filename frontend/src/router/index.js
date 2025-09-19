import { createRouter, createWebHistory } from 'vue-router';
import UnionManagementView from '../views/UnionManagementView.vue';
import PlayerDataHubView from '../views/PlayerDataHubView.vue';

const routes = [
  {
    path: '/',
    redirect: '/unions',
  },
  {
    path: '/unions',
    name: 'UnionManagement',
    component: UnionManagementView,
  },
  {
    path: '/players',
    name: 'PlayerDataHub',
    component: PlayerDataHubView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
