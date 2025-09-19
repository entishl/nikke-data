import globals from "globals";
import eslintPluginVue from 'eslint-plugin-vue';
import js from '@eslint/js';
import prettier from 'eslint-config-prettier';

export default [
  {
    // Apply browser globals to all vue and js files
    files: ["**/*.{js,vue}"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node, // Also add node globals for things like `process` if needed
      }
    }
  },
  // Recommended configs
  js.configs.recommended,
  ...eslintPluginVue.configs['flat/recommended'],
  // Prettier config to disable conflicting rules
  prettier,
  // Custom rules
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'no-undef': 'error' // Keep this on to catch real undefined variables
    },
  },
];
