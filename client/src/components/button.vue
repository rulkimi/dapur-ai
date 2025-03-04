<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'primary-outline';
  size?: 'md' | 'lg' | 'sm';
  icon?: string
  iconPosition?: 'start' | 'end'
}>();

const buttonVariant = {
  'primary': 'text-white bg-gradient-to-t to-teal-500 via-teal-600 from-teal-700 bg-size-200 bg-pos-0 hover:bg-pos-100',
  'primary-outline': 'border border-teal-500 text-teal-500 hover:bg-teal-500 hover:text-white'
};

const buttonSize = {
  'md': 'px-3 py-1',
  'lg': 'px-4 py-2',
  'sm': 'px-2 py-1'
}
</script>

<template>
  <button
    class="flex items-center gap-2 rounded-lg transition-all duration-300 w-fit"
    :class="[
      buttonSize[size ? size : 'md'],
      buttonVariant[variant ? variant : 'primary']
    ]"
  >
    <font-awesome-icon v-if="icon" :icon="['fas', icon]" />
    <slot v-else name="icon"></slot>
    <slot></slot>
  </button>
</template>