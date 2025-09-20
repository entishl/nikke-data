<template>
  <div class="toast-container">
    <Toast
      v-for="toast in toasts"
      :key="toast.id"
      :message="toast.message"
      :type="toast.type"
      :duration="toast.duration"
      @close="removeToast(toast.id)"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Toast from './Toast.vue';

const toasts = ref([]);

let idCounter = 0;

const addToast = (message, type = 'success', duration = 3000) => {
  const id = idCounter++;
  toasts.value.push({ id, message, type, duration });
  setTimeout(() => {
    removeToast(id);
  }, duration);
};

const removeToast = (id) => {
  toasts.value = toasts.value.filter((toast) => toast.id !== id);
};

defineExpose({
  addToast,
});
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>