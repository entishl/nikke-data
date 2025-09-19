import { createI18n } from 'vue-i18n';
import { useUnionStore } from '@/stores/unionStore';
import en from '../locales/en.json';
import zhHans from '../locales/zh-Hans.json';
import ja from '../locales/ja.json';
import ko from '../locales/ko.json';
import zhHant from '../locales/zh-Hant.json';

// 获取存储的语言或浏览器默认语言
const getInitialLocale = () => {
  // 注意：这个函数现在在 app.use(pinia) 之后被调用
  const unionStore = useUnionStore();
  return unionStore.locale || navigator.language || 'en';
};

const messages = {
  en,
  'zh-Hans': zhHans,
  ja,
  ko,
  'zh-Hant': zhHant,
};

const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: 'en', // 临时设置，将在 use 之后更新
  fallbackLocale: 'en',
  messages,
});

// 扩展 app.use(i18n) 的行为
const originalUse = i18n.install;
i18n.install = (app, ...options) => {
  originalUse(app, ...options);

  // 确保在 Pinia 初始化之后再获取 locale
  const initialLocale = getInitialLocale();
  i18n.global.locale.value = initialLocale;
};

export default i18n;