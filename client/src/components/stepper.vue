<script setup lang="ts">
export interface Step {
  id: string
  title: string
}

defineProps<{
  currentStep: number
  steps: Step[]
}>()

const emit = defineEmits<{
  (e: 'update:currentStep', step: number): void
}>()

const handleClick = (index: number) => {
  emit('update:currentStep', index + 1)
}
</script>

<template>
  <div class="space-y-6 mx-auto max-w-3xl">
    <ul class="flex gap-2 justify-between">
      <li
        v-for="(step, index) in steps"
        :key="index"
        class="flex-grow cursor-pointer"
        :class="currentStep >= index + 1 ? 'text-teal-500' : 'text-slate-500'"
        @click="handleClick(index)"
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
      <div v-show="index + 1 === currentStep" >
        <slot :name="step.id"></slot>
      </div>
    </div>
    <div class="flex gap-1">
      <slot name="footer"></slot>
    </div>
  </div>
</template>