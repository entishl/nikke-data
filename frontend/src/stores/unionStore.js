import { defineStore } from 'pinia';

// All data-fetching and caching logic has been migrated to TanStack Query (@tanstack/vue-query).
// This store is now responsible only for global, cross-component UI state that is not
// related to server data. For example, a theme preference, or the state of a
// non-persistent popup.

export const useUnionStore = defineStore('ui', {
  state: () => ({
    locale: localStorage.getItem('locale') || 'en',
  }),
  actions: {
    setLocale(newLocale) {
      this.locale = newLocale;
      localStorage.setItem('locale', newLocale);
    },
  },
});