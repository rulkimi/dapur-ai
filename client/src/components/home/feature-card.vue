<script setup lang="ts">
export interface Feature {
  icon: string
  title: string
  description: string
}

defineProps<{
  feature: Feature
}>()
</script>

<template>
  <div class="shadow-sm border border-gray-100 rounded-lg p-4 space-y-4 flex-grow">
    <div class="size-8 bg-teal-100 rounded-md flex justify-center items-center">
      <font-awesome-icon class="text-teal-500 text-xl" :icon="['fas', feature.icon]" />
    </div>
    <div class="space-y-2">
      <span class="block font-medium">{{ feature.title }}</span>
      <span class="block text-slate-500">{{ feature.description }}</span>
    </div>
  </div>
</template>