<script setup lang="ts">
import HeadingTitle from '../../components/heading-title.vue';
import Button from '../../components/button.vue';

import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { capitalizeFirstLetter } from '../../utils';

const route = useRoute();
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

interface RecipeListItem extends Recipe {
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
    <ul class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-3xl mx-auto">
      <li
        v-for="recipe in recipes"
        :key="recipe.id"
        class="relative rounded-xl w-fit border border-gray-200 overflow-hidden"
      >
        <div class="absolute top-2 right-4 text-white text-sm bg-teal-500 px-3 py-0.5 rounded-full">
          {{ recipe.match_percentage }}% Match
        </div>
        <img class="object-cover" :src="recipe.image_url" alt="">
        <div class="p-4 space-y-4">
          <div>
            <p class="font-semibold text-xl">{{ recipe.name }}</p>
            <p class="text-slate-500">{{ recipe.description }}</p>
          </div>
          <div class="flex justify-between gap-2">
            <p>
              <font-awesome-icon class="text-teal-500 mr-1" :icon="['fas', 'clock']" />
              {{ recipe.estimated_time_taken }} mins
            </p>
            <p>
              <font-awesome-icon class="text-teal-500 mr-1" :icon="['fas', 'wrench']" />
              {{ recipe.difficulty }}
            </p>
          </div>
          <div class="space-y-2">
            <p>Ingredients: </p>
            <ul class="flex flex-wrap gap-1">
              <li
                v-for="(ingredient, index) in recipe.ingredients"
                :key="index"
                class="bg-gray-100 px-3 py-0.5 rounded-full text-sm"
              >
                {{ capitalizeFirstLetter(ingredient) }}
              </li>
            </ul>
          </div>
          <Button
            icon="book-open"
            width="full"
          >
            View Recipe
          </Button>
        </div>
      </li>
    </ul>
  </div>
</template>