<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="text-center max-w-lg mx-auto space-y-1">
    <h1 class="text-3xl font-semibold">{{ title }}</h1>
    <span v-if="subtitle" class="block text-slate-500">{{ subtitle }}</span>
  </div>
</template>