<script setup lang="ts">
import { capitalizeFirstLetter } from '../../utils'

const props = defineProps<{
  modelValue: string[]
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
  <ul class="grid grid-cols-2 md:grid-cols-4 gap-y-1">
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
</template>