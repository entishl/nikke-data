<template>
  <button
    :type="type"
    :disabled="disabled"
    @click="$emit('click')"
    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
    :class="{ 'opacity-50 cursor-not-allowed': disabled }"
  >
    <slot></slot>
  </button>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  type: {
    type: String,
    default: 'button',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['click']);
</script>