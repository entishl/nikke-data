<template>
  <div class="language-switcher">
    <button @click="setLocale('zh-Hans')">简体中文</button>
    <button @click="setLocale('en')">English</button>
    <button @click="setLocale('ja')">日本語</button>
    <button @click="setLocale('ko')">한국어</button>
    <button @click="setLocale('zh-Hant')">繁體中文</button>
  </div>
</template>

<script setup>
import { useLocale } from '@/composables/useLocale';

const { setLocale } = useLocale();
</script>

<style scoped>
.language-switcher {
  margin: 1rem;
}
button {
  margin-right: 0.5rem;
}
</style>