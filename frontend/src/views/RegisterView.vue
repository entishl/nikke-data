<template>
  <div class="register-view">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
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
      <BaseButton type="submit">Register</BaseButton>
    </form>
    <p v-if="message" :class="isSuccess ? 'success-message' : 'error-message'">{{ message }}</p>
     <p>
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import BaseInput from '@/components/BaseInput.vue';
import BaseButton from '@/components/BaseButton.vue';

const username = ref('');
const password = ref('');
const message = ref('');
const isSuccess = ref(false);

const router = useRouter();
const authStore = useAuthStore();

const handleRegister = async () => {
  try {
    await authStore.register(username.value, password.value);
    isSuccess.value = true;
    message.value = 'Registration successful! Redirecting to login...';
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } catch (error) {
    isSuccess.value = false;
    message.value = authStore.error || 'Registration failed. Please try again.';
    console.error(error);
  }
};
</script>

<style scoped>
.register-view {
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

.success-message {
  color: green;
  margin-top: 15px;
}
</style>