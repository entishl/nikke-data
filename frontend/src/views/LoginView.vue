<template>
  <div class="login-view">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <BaseInput
        id="username"
        v-model="username"
        label="Username"
        type="text"
        placeholder="Enter your username"
        required
      />
      <BaseInput
        id="password"
        v-model="password"
        label="Password"
        type="password"
        placeholder="Enter your password"
        required
      />
      <BaseButton type="submit">Login</BaseButton>
    </form>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p>
      Don't have an account? <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import BaseInput from '@/components/BaseInput.vue';
import BaseButton from '@/components/BaseButton.vue';

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const handleLogin = async () => {
  try {
    await authStore.login(username.value, password.value, router, route);
  } catch (error) {
    errorMessage.value = 'Failed to login. Please check your credentials.';
    console.error(error);
  }
};
</script>

<style scoped>
.login-view {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.error-message {
  color: red;
  margin-top: 15px;
}

.error-message {
  color: red;
  margin-top: 15px;
}
</style>