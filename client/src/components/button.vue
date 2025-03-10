<script setup lang="ts">
import { type ButtonHTMLAttributes, ref } from 'vue';

interface ButtonProps {
  variant?: 'primary' | 'primary-outline' | 'link';
  size?: 'md' | 'lg' | 'sm';
  icon?: string
  hoverIcon?: string
  iconPosition?: 'start' | 'end'
  width?: 'fit' | 'full'
  type?: ButtonHTMLAttributes['type']
  disabled?: boolean
  loading?: boolean
}

withDefaults(defineProps<ButtonProps>(), {
  variant: 'primary',
  size: 'md',
  width: 'fit',
  type: 'button',
  disabled: false
})

const buttonVariant = {
  'primary': {
    default: 'text-white bg-gradient-to-t to-teal-400 via-teal-500 from-teal-600 bg-size-200 bg-pos-0',
    hover: 'hover:bg-pos-100'
  } ,
  'primary-outline': {
    default: 'border border-teal-500 text-teal-500',
    hover: 'hover:bg-teal-500 hover:text-white'
  },
  'link': {
    default: '!inline !px-0 text-teal-500',
    hover: 'hover:underline'
  }
};

const buttonSize = {
  'md': 'px-3 py-1 h-[36px]',
  'lg': 'px-4 py-2 h-[46px]',
  'sm': 'px-2 py-1 h-[28px]'
}

const buttonWidth = {
  'fit' : 'w-fit',
  'full' : 'w-full justify-center'
}

const isHovered = ref<boolean>(false)
const hoverTimeout = ref< number | null >(null)

const handleMouseOver = () => {
  isHovered.value = true
}

const handleMouseOut = () => {
  if (hoverTimeout.value) clearTimeout(hoverTimeout.value)
  hoverTimeout.value = window.setTimeout(() => {
    isHovered.value = false
  }, 300)
}
</script>

<template>
  <button
    class="flex items-center gap-2 rounded-lg transition-all duration-300"
    :class="[
      buttonSize[size],
      buttonVariant[variant].default,
      buttonWidth[width],
      disabled || loading ? 'opacity-50 cursor-not-allowed' : buttonVariant[variant].hover
    ]"
    :type="type"
    :disabled="disabled"
    @mouseenter="handleMouseOver"
    @mouseleave="handleMouseOut"
  >
    <Transition v-if="icon" name="icon" mode="out-in">
      <font-awesome-icon v-if="isHovered && hoverIcon" :icon="['fas', hoverIcon]" :key="hoverIcon" />
      <font-awesome-icon v-else-if="loading" class="animate-spin" :icon="['fas', 'circle-notch']" />
      <font-awesome-icon v-else :icon="['fas', icon]" :key="icon" />
    </Transition>
    <slot v-else name="icon"></slot>
    <slot></slot>
  </button>
</template>

<style scoped>
.icon-enter-active  {
  transition: transform 0.1s;
}
.icon-leave-active {
  transition: transform 0.05s;
}
.icon-enter-from {
  transform: scale(0.5);
}
.icon-leave-to {
  transform: scale(0.5);
}
</style>