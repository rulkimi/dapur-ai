<script setup lang="ts">
import { capitalizeFirstLetter } from '../../../utils'

const props = defineProps<{
  modelValue: string[]
  readonly?: boolean
}>()
const emit = defineEmits(['update:modelValue'])

const cuisineExamples: string[] = [
  "melayu",
  "cina",
  "india",
  "indonesia",
  "asia",
  "barat",
  "arab",
  "itali"
]
const handleCuisines = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const isChecked = target.checked;
  const value = target.id;
  const newValue = isChecked ? [...props.modelValue, value] : props.modelValue.filter((item: string) => item !== value);
  emit('update:modelValue', newValue);
};
</script>

<template>
  <ul v-if="!readonly" class="grid grid-cols-2 gap-y-1">
    <li
      v-for="cuisine in cuisineExamples"
      :key="cuisine"
      class="flex items-baseline gap-2"
    >
      <input
        type="checkbox"
        :id="cuisine"
        @change="handleCuisines"
      >
      <label :for="cuisine">{{ capitalizeFirstLetter(cuisine) }}</label>
    </li>
  </ul>
  <ul class="flex flex-wrap gap-1" v-else>
    <li
      v-for="cuisine in modelValue"
      :key="cuisine"
      class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
    >
      {{ capitalizeFirstLetter(cuisine) }}
    </li>
  </ul>
</template>