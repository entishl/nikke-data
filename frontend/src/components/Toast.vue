<template>
  <div v-if="visible" :class="['toast', `toast-${type}`]">
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'success', // success, error
  },
  duration: {
    type: Number,
    default: 3000,
  },
});

const visible = ref(false);

onMounted(() => {
  visible.value = true;
  setTimeout(() => {
    visible.value = false;
  }, props.duration);
});
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  z-index: 1000;
  transition: all 0.3s ease;
}

.toast-success {
  background-color: #4caf50;
}

.toast-error {
  background-color: #f44336;
}
</style>