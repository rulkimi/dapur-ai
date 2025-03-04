<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="space-y-2">
    <div>
      <h3 class="text-xl font-semibold">{{ title }}</h3>
      <span v-if="subtitle" class="block text-slate-500">{{ subtitle }}</span>
    </div>
    <div class="space-y-2">
      <slot></slot>
    </div>
  </div>
</template>