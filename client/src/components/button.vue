<script setup lang="ts">
import type { ButtonHTMLAttributes } from 'vue';

interface ButtonProps {
  variant?: 'primary' | 'primary-outline';
  size?: 'md' | 'lg' | 'sm';
  icon?: string
  iconPosition?: 'start' | 'end'
  width?: 'fit' | 'full'
  type?: ButtonHTMLAttributes['type']
}

withDefaults(defineProps<ButtonProps>(), {
  variant: 'primary',
  size: 'md',
  width: 'fit',
  type: 'button'
})

const buttonVariant = {
  'primary': 'text-white bg-gradient-to-t to-teal-400 via-teal-500 from-teal-600 bg-size-200 bg-pos-0 hover:bg-pos-100',
  'primary-outline': 'border border-teal-500 text-teal-500 hover:bg-teal-500 hover:text-white'
};

const buttonSize = {
  'md': 'px-3 py-1 h-[36px]',
  'lg': 'px-4 py-2 h-[46px]',
  'sm': 'px-2 py-1 h-[32px]'
}

const buttonWidth = {
  'fit' : 'w-fit',
  'full' : 'w-full justify-center'
}
</script>

<template>
  <button
    class="flex items-center gap-2 rounded-lg transition-all duration-300"
    :class="[
      buttonSize[size],
      buttonVariant[variant],
      buttonWidth[width]
    ]"
    :type="type"
  >
    <font-awesome-icon v-if="icon" :icon="['fas', icon]" />
    <slot v-else name="icon"></slot>
    <slot></slot>
  </button>
</template>