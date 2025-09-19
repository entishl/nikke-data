<template>
  <div class="register-view">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
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
import { register } from '@/services/api';

const username = ref('');
const password = ref('');
const message = ref('');
const isSuccess = ref(false);

const router = useRouter();

const handleRegister = async () => {
  try {
    await register({ username: username.value, password: password.value });
    isSuccess.value = true;
    message.value = 'Registration successful! Redirecting to login...';
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } catch (error) {
    isSuccess.value = false;
    message.value = 'Registration failed. Please try again.';
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

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #218838;
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