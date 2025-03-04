<script setup lang="ts">
import Button from '../components/button.vue';
import PreferenceLayout from '../layouts/preference-layout.vue';
import Allergies from '../components/preferences/allergies.vue';
import { ref } from 'vue';
import { capitalizeFirstLetter } from '../utils';

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
const dietaryRestrictions = ref<string[]>([]);
const handleDietaryRestrictions = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const isChecked = target.checked;
  const value = target.id;
  const newValue = isChecked ? [...dietaryRestrictions.value, value] : dietaryRestrictions.value.filter((item) => item !== value);
  dietaryRestrictions.value = newValue;
};

const cuisineExamples: string[] = [
  "melayu",
  "cina",
  "india",
  "indonesia",
  "asia",
  "barat",
  "arab",
  "itali"
]
const prefferedCuisines = ref<string[]>([])
const handleCuisines = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const isChecked = target.checked;
  const value = target.id;
  const newValue = isChecked ? [...prefferedCuisines.value, value] : prefferedCuisines.value.filter((item) => item !== value);
  prefferedCuisines.value = newValue;
};


const allergies = ref<string[]>([])

interface PreferredSpice {
  name: string
  description: string
}
const preferredSpices: PreferredSpice[] = [
  { name: 'mild', description: 'Saya lebih suka sedikit atau tiada pedas.' },
  { name: 'medium', description: 'Saya gemar tahap kepedasan sederhana.' },
  { name: 'hot', description: 'Saya suka makanan pedas!' }
]
const preferredSpice = ref<string>('mild')

const savePreferences = () => {
  const food_preferences = {
    dietary_restrictions: dietaryRestrictions.value,
    allergies: allergies.value,
    preferred_cuisines: prefferedCuisines.value,
    spice_level: preferredSpice.value
  }
  console.table(food_preferences)
}
</script>

<template>
  <div class="custom-card space-y-6 max-w-3xl mx-auto">
    <div class="text-center">
      <h2 class="text-2xl font-semibold">Kongsikan citarasa anda dengan kami</h2>
      <span class="block text-slate-500">Kami akan cadangkan resipi yang sesuai dengan selara anda</span>
    </div>

    <form @submit.prevent="savePreferences">
      <PreferenceLayout
        title="Ada sebarang keperluan diet?"
        subtitle="Pilih semua yang berkaitan"
      >
        <ul class="grid grid-cols-4 gap-y-1">
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
      </PreferenceLayout>
      <PreferenceLayout title="Ada sebarang alahan atau bahan yang ingin dielakkan?">
        <Allergies v-model="allergies" />
      </PreferenceLayout>
      
      <PreferenceLayout
        title="Masakan mana yang ada gemari?"
        subtitle="Pilih semua yang berkaitan"
      >
        <ul class="grid grid-cols-2 gap-y-1">
          <li
            v-for="cuisine in cuisineExamples"
            :key="cuisine"
            class="flex items-baseline gap-2"
          >
            <input
              type="checkbox"
              :id="cuisine"
              @change="handleCuisines"
            >
            <label :for="cuisine">{{ capitalizeFirstLetter(cuisine) }}</label>
          </li>
        </ul>
      </PreferenceLayout>
      <PreferenceLayout title="Sejauh mana tahap kepedasan yang anda suka?">
        <ul>
          <li
            v-for="spice in preferredSpices"
            :key="spice.name"
            class="flex items-center gap-2"
          >
            <input
              type="radio"
              :id="spice.name"
              :value="spice.name"
              name="spice-level"
              v-model="preferredSpice"
            >
            <label :for="spice.name">
              {{ capitalizeFirstLetter(spice.name) }} - {{ spice.description }}
            </label>
          </li>
        </ul>
      </PreferenceLayout>
      <div class="flex justify-end">
        <Button icon="bookmark" type="submit">
          Simpan Citarasa
        </Button>
      </div>
    </form>

  </div>
</template>