<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="space-y-2 md:space-y-0 md:grid md:grid-cols-5 md:gap-4 border-b py-6">
    <div class="md:col-span-2">
      <h3 class="text-xl font-semibold">{{ title }}</h3>
      <span v-if="subtitle" class="block text-slate-500">{{ subtitle }}</span>
    </div>
    <div class="space-y-2 py-4 md:col-span-3">
      <slot></slot>
    </div>
  </div>
</template>