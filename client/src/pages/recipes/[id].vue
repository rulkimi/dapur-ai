<script setup lang="ts">
import HeadingTitle from '../../components/heading-title.vue';
import Button from '../../components/button.vue';
import RecipeDetailComponent from '../../components/recipes/recipe-detail.vue';

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
  difficulty: 'Easy' | 'Medium' | 'Difficult'
  tags: string[]
}

export interface RecipeListItem extends Recipe {
  ingredients: string[]
  match_percentage: number
  estimated_time_taken: number
}

export interface RecipeDetail extends Recipe {
  prep_time: number
  cooking_time: number
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
const recipeDetail = ref<RecipeDetail | null>(null)
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

const recipeDetailSample: RecipeDetail = {
  id: '1',
  name: 'Nasi Goreng',
  image_url: 'https://placehold.co/600x400',
  description: 'Nasi goreng is a popular Indonesian dish. It is usually made with fried rice, chicken, egg, and onion.',
  prep_time: 10,
  cooking_time: 15,
  difficulty: 'Easy',
  ingredients: [
    {
      name: 'Nasi',
      amount: 2,
      measurement: 'cups'
    },
    {
      name: 'Ayam',
      amount: 100,
      measurement: 'grams'
    },
    {
      name: 'Telur',
      amount: 2,
      measurement: 'pcs'
    },
    {
      name: 'Bawang',
      amount: 2,
      measurement: 'unit'
    }
  ],
  instructions: [
    'Heat oil in a wok.',
    'Add chicken and fry until cooked.',
    'Add rice and fry until heated through.',
    'Add egg and fry until cooked.',
    'Add onion and fry until softened.',
    'Serve hot.'
  ],
  nutrition: [
    {
      name: 'Calories',
      value: '300'
    },
    {
      name: 'Protein',
      value: '20g'
    },
    {
      name: 'Fat',
      value: '10g'
    },
    {
      name: 'Carbohydrates',
      value: '40g'
    }
  ],
  tags: ['Malaysian', 'Chicken', 'Rice'],
}
recipeDetail.value = recipeDetailSample;


const showDrawer = ref<boolean>(true);
const viewRecipe = (id: string) => {
  console.log(id)
  showDrawer.value = true;
}
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
        @mouseenter="console.log(recipe.id)"
        @mouseleave="console.log(recipe.id)"
      >
        <RecipeCard :recipe="recipe" @view-recipe="viewRecipe" />
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

  <div
    class="fixed bg-white border border-gray-200 inset-0 transition-transform duration-300 rounded-3xl p-6"
    :class="showDrawer ? 'translate-y-[80px]' : 'translate-y-[900px]'"
  >
    <RecipeDetailComponent
      v-if="recipeDetail"
      :recipe-detail="recipeDetail"
      @close="showDrawer = false"
    />
  </div>
</template>