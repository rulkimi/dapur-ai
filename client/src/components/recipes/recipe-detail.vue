<script setup lang="ts">
import Button from "../button.vue";
import Tabs from "../tabs.vue";

import { ref } from "vue";
import { type RecipeDetail } from "../../pages/recipes/detail/[recipeId].vue";

defineProps<{
  recipeDetail: RecipeDetail;
}>();

// const emit = defineEmits(["close"]);
const servings = ref<number>(2);

const tabItems = [
  { title: "ingredients" },
  { title: "instructions" },
  { title: "nutrition" },
];
const activeTab = ref<string>("ingredients");

const countAmountByServings = (amount: number): number => {
  return amount * servings.value;
}
</script>

<template>
  <div v-if="recipeDetail" class="space-y-6 max-w-3xl mx-auto">
    <div>
      <div class="flex justify-between">
        <h2 class="text-2xl font-semibold">{{ recipeDetail.name }}</h2>
        <!-- <font-awesome-icon
          class="cursor-pointer text-2xl hover:scale-110 transition-transform duration-300"
          :icon="['fas', 'times']"
          @click="emit('close')"
        /> -->
      </div>
      <p class="text-slate-500">{{ recipeDetail.description }}</p>
    </div>
    <img :src="recipeDetail.image_url" class="rounded-xl h-48 w-full object-cover" />
    <ul class="flex flex-wrap gap-2 justify-between text-slate-500">
      <li>
        <font-awesome-icon
          class="text-teal-500 mr-1"
          :icon="['fas', 'clock']"
        />
        {{ recipeDetail.prep_time }} mins
      </li>
      <li>
        <font-awesome-icon
          class="text-teal-500 mr-1"
          :icon="['fas', 'utensils']"
        />
        {{ recipeDetail.cooking_time }} mins
      </li>
      <li class="flex items-center gap-2">
        <font-awesome-icon
          class="text-teal-500 mr-1"
          :icon="['fas', 'users']"
        />
        Servings:
        <span class="flex items-center gap-2">
          <Button
            variant="primary-outline"
            size="sm"
            @click="servings = Math.max(1, servings - 1)"
            >-</Button
          >
          <div class="w-[24px] flex justify-center">{{ servings }}</div>
          <Button variant="primary-outline" size="sm" @click="servings++"
            >+</Button
          >
        </span>
      </li>
      <li>
        <font-awesome-icon
          class="text-teal-500 mr-1"
          :icon="['fas', 'wrench']"
        />
        {{ recipeDetail.difficulty }}
      </li>
    </ul>
    <ul class="flex flex-wrap gap-2">
      <li
        v-for="(tag, index) in recipeDetail.tags"
        :key="index"
        class="text-sm bg-gray-200 px-3 py-0.5 rounded-full"
      >
        {{ tag }}
      </li>
    </ul>
    <Tabs v-model="activeTab" :tabs="tabItems">
      <template #ingredients>
        <ul class="space-y-2">
          <li
            v-for="(ingredient, index) in recipeDetail.ingredients"
            :key="index"
          >
            <div class="flex justify-between">
              <p>{{ ingredient.name }}</p>
              <p class="text-slate-500">
                {{ countAmountByServings(ingredient.amount) }} {{ ingredient.measurement }}
              </p>
            </div>
          </li>
        </ul>
      </template>
      <template #instructions>
        <ul class="space-y-2">
          <li
            v-for="(instruction, index) in recipeDetail.instructions"
            :key="index"
            class="list-decimal ml-4"
          >
            {{ instruction }}
          </li>
        </ul>
      </template>
      <template #nutrition>

      </template>
    </Tabs>
  </div>
</template>
