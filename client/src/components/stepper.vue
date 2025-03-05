<script setup lang="ts">
export interface Step {
  title: string
}

defineProps<{
  currentStep: number
  steps: Step[]
}>()
</script>

<template>
  <div class="space-y-6">
    <ul class="flex gap-2 justify-between max-w-2xl mx-auto">
      <li
        v-for="(step, index) in steps"
        :key="index"
        class="flex-grow"
        :class="currentStep >= index + 1 ? 'text-teal-500' : 'text-slate-500'"
      >
        <div
          class="h-1 rounded-full mb-1"
          :class="currentStep >= index + 1 ? 'bg-teal-500' : 'bg-gray-200'"
        ></div>
        <span>{{ step.title }}</span>
      </li>
    </ul>
    <div
      v-for="(step, index) in steps"
      :key="index"
    >
      <div v-if="index + 1 === currentStep">
        <slot name="content" :step="step"></slot>
      </div>
    </div>
    <div class="flex gap-1">
      <slot name="footer"></slot>
    </div>
  </div>
</template>