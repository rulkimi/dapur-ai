<script setup lang="ts">
import Button from '../components/button.vue';
import PreferenceLayout from '../layouts/preference-layout.vue';
import Allergies from '../components/preferences/allergies.vue';
import { ref } from 'vue';
import { capitalizeFirstLetter } from '../utils';

const dietaryRestrictions: string[] = [
  "vegetarian",
  "vegan",
  "bebas gluten",
  "bebas tenusu",
  "keto",
  "paleo",
  "rendah karbohidrat",
  "rendah lemak"
]

const cuisines: string[] = [
  "melayu",
  "cina",
  "india",
  "indonesia",
  "asia",
  "barat",
  "arab",
  "itali"
]

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
</script>

<template>
  <div class="custom-card space-y-6 max-w-3xl mx-auto">
    <div class="text-center">
      <h2 class="text-2xl font-semibold">Kongsikan citarasa anda dengan kami</h2>
      <span class="block text-slate-500">Kami akan cadangkan resipi yang sesuai dengan selara anda</span>
    </div>

    <PreferenceLayout
      title="Ada sebarang keperluan diet?"
      subtitle="Pilih semua yang berkaitan"
    >
      <ul class="grid grid-cols-4 gap-y-1">
        <li
          v-for="diet in dietaryRestrictions"
          :key="diet"
          class="flex items-baseline gap-2"
        >
          <input type="checkbox" :id="diet" class="border border-teal-500 rounded">
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
          v-for="cuisine in cuisines"
          :key="cuisine"
          class="flex items-baseline gap-2"
        >
          <input type="checkbox" :id="cuisine" class="border border-teal-500 rounded">
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
      <Button icon="bookmark">
        Simpan Citarasa
      </Button>
    </div>
  </div>
</template>