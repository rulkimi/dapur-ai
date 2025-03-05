<script setup lang="ts">
import HeadingTitle from '../../components/heading-title.vue';
import Button from '../../components/button.vue';

import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import RecipeCard from '../../components/recipes/recipe-card.vue';

const route = useRoute();
const router = useRouter();
const recipeId = route.params.id;

interface Recipe {
  id: string
  name: string
  image_url: string
  description: string
  estimated_time_taken: number
  difficulty: 'Easy' | 'Medium' | 'Difficult'
  match_percentage: number
  tags: string[]
}

export interface RecipeListItem extends Recipe {
  ingredients: string[]
}

interface RecipeDetail extends Recipe {
  ingredients: Array<{
    name: string
    amount: number
    measurement: string
  }>
  instructions: string[]
  nutrition: Array<{
    name: string
    value: string
  }>
}

const recipes = ref<RecipeListItem[]>([])
console.log(recipeId);

const recipeList: RecipeListItem[] = [
  {
    id: '1',
    name: 'Nasi Goreng',
    image_url: 'https://placehold.co/600x400',
    description: 'Nasi goreng is a popular Indonesian dish.',
    estimated_time_taken: 20,
    difficulty: 'Easy',
    match_percentage: 80,
    tags: ['Indonesian', 'Rice', 'Easy'],
    ingredients: ['nasi', 'ayam', 'telur', 'bawang']
  },
  {
    id: '2',
    name: 'Ayam Masak Merah',
    image_url: 'https://placehold.co/600x400',
    description: 'Ayam masak merah is a spicy chicken dish.',
    estimated_time_taken: 30,
    difficulty: 'Medium',
    match_percentage: 70,
    tags: ['Malaysian', 'Chicken', 'Spicy'],
    ingredients: ['ayam', 'bawang putih', 'lada benggala']
  },
  {
    id: '3',
    name: 'Mee Goreng Mamak',
    image_url: 'https://placehold.co/600x400',
    description: 'Mee goreng mamak is a Malaysian noodle dish.',
    estimated_time_taken: 25,
    difficulty: 'Medium',
    match_percentage: 60,
    tags: ['Malaysian', 'Noodles', 'Spicy'],
    ingredients: ['mee', 'ayam', 'telur', 'bawang']
  }
]
recipes.value = recipeList;
</script>

<template>
  <div class="space-y-6">
    <HeadingTitle 
      title="Resipi untuk Anda"
      :subtitle="`Kami jumpa ${recipes.length} resipi yang anda boleh buat dengan bahan yang ada.`"
    />
    <ul class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
      <li
        v-for="recipe in recipes"
        :key="recipe.id"
        class="w-fit border border-transparent"
      >
        <RecipeCard :recipe="recipe" />
      </li>
    </ul>
    <Button
      variant="primary-outline"
      icon="arrow-left"
      class="mx-auto"
      size="lg"
      @click="router.push('/recipes')"
    >
      Tukar Bahan
    </Button>
  </div>
</template>