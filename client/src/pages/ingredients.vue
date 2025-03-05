<script setup lang="ts">
import FormInput from '../components/form-input.vue';
import Button from '../components/button.vue';

import { ref } from 'vue';
import { capitalizeFirstLetter } from '../utils';

const ingredient = ref<string>('')
const ingredients = ref<string[]>([])
const commonIngredients: string[] = [
  'nasi',
  'ayam',
  'telur',
  'bawang',
  'bawang putih',
  'tomato',
  'kentang',
  'lobak merah',
  'daging lembu',
  'ikan',
  'udang',
  'bayam',
  'brokoli',
  'lada benggala',
  'lemon'
]

const handleEnterKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && ingredient.value.trim() !== '') addIngredient(ingredient.value);
}
const addIngredient = (newIngredient: string) => {
  if (newIngredient === '') return;
  if (ingredients.value.includes(newIngredient)) {
    ingredient.value = ''
    return
  }
  ingredients.value = [...ingredients.value, newIngredient]
  ingredient.value = ''
}
const removeIngredient = (index: number) => {
  ingredients.value = ingredients.value.filter((_, i) => i !== index);
}
</script>

<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <div class="text-center max-w-lg mx-auto space-y-1">
      <h1 class="text-3xl font-semibold">Bahan apa yang anda ada?</h1>
      <span class="block text-slate-500">Senaraikan bahan sedia ada dan kami akan cadangkan resipi yang boleh anda buat!</span>
    </div>
    <div class="flex items-center gap-1">
      <FormInput
        id="ingredient"
        v-model="ingredient"
        class="flex-grow"
        size="lg"
        placeholder="Taipkan satu bahan..."
        @keyup.enter="handleEnterKeydown"
      />
      <Button
        variant="primary-outline"
        icon="plus"
        size="lg"
        @click="addIngredient(ingredient)"
      >
        Tambah
      </Button>
    </div>
    <div class="space-y-1">
      <span class="block text-slate-500">Bahan biasa:</span>
      <ul class="flex flex-wrap gap-1">
        <li
          v-for="ingredient in commonIngredients"
          :key="ingredient"
          class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
          @click="addIngredient(ingredient)"
        >
          {{ capitalizeFirstLetter(ingredient) }}
        </li>
      </ul>
    </div>
    
    <div class="space-y-1">
      <span v-if="ingredients.length" class="block text-slate-500">Bahan anda:</span>
      <ul class="flex flex-wrap gap-1">
        <li
          v-for="(ingredient, index) in ingredients"
          :key="ingredient"
          class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
        >
          {{ capitalizeFirstLetter(ingredient) }}
          <font-awesome-icon
            class="hover:scale-110 hover:text-slate-800 transition-all duration-300"
            :icon="['fas', 'times']"
            @click="removeIngredient(index)"
          />
        </li>
      </ul>
    </div>
    
    <Button
      class="mx-auto"
      icon="magnifying-glass"
      size="lg"
    >
      Cari Resipi
    </Button>
  </div>
</template>