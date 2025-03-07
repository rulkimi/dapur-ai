<script setup lang="ts">
import { capitalizeFirstLetter } from '../../../utils'

const props = defineProps<{
  modelValue: string[]
  readonly?: boolean
}>()

const emits = defineEmits(['update:modelValue'])

const dietaryRestrictionExamples: string[] = [
  "vegetarian",
  "vegan",
  "bebas gluten",
  "bebas tenusu",
  "keto",
  "paleo",
  "rendah karbohidrat",
  "rendah lemak"
]
const handleDietaryRestrictions = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const isChecked = target.checked;
  const value = target.id;
  const newValue = isChecked ? [...props.modelValue, value] : props.modelValue.filter((item) => item !== value);
  emits('update:modelValue', newValue);
};
</script>

<template>
  <ul v-if="!readonly" class="grid grid-cols-2 md:grid-cols-4 gap-y-1">
    <li
      v-for="diet in dietaryRestrictionExamples"
      :key="diet"
      class="flex items-baseline gap-2"
    >
      <input
        type="checkbox"
        :id="diet"
        @change="handleDietaryRestrictions"
      >
      <label :for="diet">{{ capitalizeFirstLetter(diet) }}</label>
    </li>
  </ul>
  <ul class="flex flex-wrap gap-1" v-else>
    <li
      v-for="diet in modelValue"
      :key="diet"
      class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
    >
      {{ capitalizeFirstLetter(diet) }}
    </li>
  </ul>
</template>