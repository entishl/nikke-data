import { defineStore } from 'pinia';
import { login as apiLogin, register as apiRegister } from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password, router, route) {
      const response = await apiLogin({ username, password });
      console.log('AuthStore: Token received from backend:', response.data.access_token);
      this.token = response.data.access_token;
      localStorage.setItem('token', response.data.access_token);
      console.log('AuthStore: Token saved to localStorage.');

      const redirectPath = route.query.redirect;
      if (redirectPath) {
        router.push(redirectPath);
      } else {
        router.push('/');
      }
    },
    async register(username, password) {
      try {
        await apiRegister({ username, password });
        this.error = null;
      } catch (error) {
        this.error = error.response.data.detail || 'Registration failed';
        throw error;
      }
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