<script setup lang="ts">
import { ref } from 'vue'
import { type Recipe } from '../[searchId].vue'
import RecipeDetailComponent from '../../../components/recipes/recipe-detail.vue'

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

const recipeDetail = ref<RecipeDetail | null>(null)
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
</script>

<template>
  <RecipeDetailComponent
    v-if="recipeDetail"
    :recipe-detail="recipeDetail"
  />
</template>