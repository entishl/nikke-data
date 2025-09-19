import { defineStore } from 'pinia';
import { login as apiLogin } from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      const response = await apiLogin({ username, password });
      console.log('AuthStore: Token received from backend:', response.data.access_token);
      this.token = response.data.access_token;
      localStorage.setItem('token', response.data.access_token);
      console.log('AuthStore: Token saved to localStorage.');
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
    },
    setUser(user) {
      this.user = user;
    },
  },
});