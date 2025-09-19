import { useI18n } from 'vue-i18n';
import { useUnionStore } from '@/stores/unionStore';
import i18n from '@/plugins/i18n';

// 动态加载语言文件的函数
const loadLocaleMessages = async (locale) => {
  const messages = await import(`../locales/${locale}.json`);
  return messages.default;
};

export function useLocale() {
  const { locale } = useI18n();
  const unionStore = useUnionStore();

  const setLocale = async (newLocale) => {
    // 加载新的语言文件
    const messages = await loadLocaleMessages(newLocale);
    
    // 设置 i18n 实例的语言
    i18n.global.setLocaleMessage(newLocale, messages);
    i18n.global.locale.value = newLocale;
    
    // 更新 Pinia store
    unionStore.setLocale(newLocale);
    
    // 更新 HTML lang 属性
    document.querySelector('html').setAttribute('lang', newLocale);
  };

  return {
    setLocale,
    currentLocale: locale,
  };
}