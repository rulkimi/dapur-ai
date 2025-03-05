<script setup lang="ts">
import { capitalizeFirstLetter } from '../utils'

defineProps<{
  modelValue: string
  tabs: Array<{
    title: string
  }>
}>()

const emit = defineEmits(['update:modelValue'])
const setActiveTab = (tabTitle: string) => {
  emit('update:modelValue', tabTitle);
}
</script>

<template>
  <div class="bg-gray-200 p-1 rounded-lg">
    <ul class="flex justify-between gap-2">
      <li
        v-for="tab in tabs"
        :item="tab.title"
        class="text-center flex-grow p-1 rounded-md cursor-pointer"
        :class="modelValue === tab.title ? 'bg-white' : ''"
        @click="setActiveTab(tab.title)"
      >
        {{ capitalizeFirstLetter(tab.title) }}
      </li>
    </ul>
  </div>
  <div
    v-if="modelValue"
    class="border border-gray-200 rounded-lg p-4"
  >
    <slot :name="modelValue"></slot>
  </div>
</template>