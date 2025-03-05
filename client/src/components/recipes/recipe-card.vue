<script setup lang="ts">
import Button from "../button.vue";
import type { RecipeListItem } from "../../pages/recipes/[searchId].vue";
import { capitalizeFirstLetter } from "../../utils";

defineProps<{
  recipe: RecipeListItem;
}>();

const emit = defineEmits(["view-recipe"]);
</script>

<template>
  <div class="relative rounded-xl w-fit border border-gray-200 overflow-hidden">
    <div
      class="absolute top-2 right-4 text-white text-sm bg-teal-500 px-3 py-0.5 rounded-full"
    >
      {{ recipe.match_percentage }}% Match
    </div>
    <img class="object-cover" :src="recipe.image_url" alt="" />
    <div class="p-4 flex flex-col gap-4">
      <div>
        <p class="font-semibold text-xl">{{ recipe.name }}</p>
        <p class="text-slate-500">{{ recipe.description }}</p>
      </div>
      <div class="flex justify-between gap-2">
        <p>
          <font-awesome-icon
            class="text-teal-500 mr-1"
            :icon="['fas', 'clock']"
          />
          {{ recipe.estimated_time_taken }} mins
        </p>
        <p>
          <font-awesome-icon
            class="text-teal-500 mr-1"
            :icon="['fas', 'wrench']"
          />
          {{ recipe.difficulty }}
        </p>
      </div>
      <div class="space-y-2">
        <p>Ingredients:</p>
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
        icon="book"
        hover-icon="book-open"
        width="full"
        @click="emit('view-recipe', recipe.id)"
      >
        View Recipe
      </Button>
    </div>
  </div>
</template>
