<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'primary-outline';
}>();

const buttonClasses = {
  'primary': 'bg-gradient-to-b from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white',
  'primary-outline': 'border border-teal-500 text-teal-500 hover:bg-teal-500 hover:text-white'
};
</script>

<template>
  <button
    class="flex items-center gap-2 px-3 py-1 rounded-lg transition-colors duration-300"
    :class="buttonClasses[variant ? variant : 'primary']"
  >
    <slot></slot>
  </button>
</template>