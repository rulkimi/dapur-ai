<script setup lang="ts">
import FormInput from '../../components/form-input.vue';
import Button from '../../components/button.vue';
import HeadingTitle from '../../components/heading-title.vue';

import { onBeforeMount, ref } from 'vue';
import { useRouter } from 'vue-router';
import { capitalizeFirstLetter } from '../../utils';

onBeforeMount(() => document.title = 'Cari Resipi - DapurAI')

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

const router = useRouter()
const loading = ref<boolean>(false)
const searchRecipe = async () => {
  loading.value = true;
  try {
    const searchId = Math.random().toString(36).substring(2, 15);
    await new Promise(resolve => setTimeout(resolve, 3000))
    router.push(`/recipes/${searchId}`)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = true
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <template v-if="!loading">
      <HeadingTitle
        title="Bahan apa yang anda ada?"
        subtitle="Senaraikan bahan sedia ada dan kami akan cadangkan resipi yang boleh anda buat!"
      />
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
          :disabled="!ingredient"
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
            class="cursor-pointer rounded-md px-2 py-0.5"
            :class="ingredients.includes(ingredient) ? 'bg-teal-100 text-teal-500' : 'bg-gray-100 hover:bg-gray-200 text-slate-600 '"
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
        @click="searchRecipe"
        :disabled="!ingredients.length"
      >
        Cari Resipi
      </Button>
    </template>
    <template v-else>
      <div class="flex flex-col gap-2 items-center justify-center my-24">
        <!-- <svg class="size-48 text-teal-500" viewBox="0 0 50 50">
          <circle cx="25" cy="25" r="10" fill="none" stroke-width="2" stroke-linecap="round" stroke="currentColor" stroke-dasharray="55 10" transform="rotate(-90 25 25)">
            <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/>
          </circle>
        </svg> -->
        <font-awesome-icon class="text-teal-500 animate-spin" :icon="['fas', 'circle-notch']" size="2xl" />
        <p class="font-semibold text-xl">Mencari resipi anda...</p>
        <p class="text-slate-500">DapurAI sedang menganalisis bahan anda untuk mencari resipi terbaik.</p>
      </div>
    </template>
  </div>
</template>