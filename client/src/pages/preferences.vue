<script setup lang="ts">
import Button from '../components/button.vue';
import FormInput from '../components/form-input.vue';
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

const allergy = ref<string>('')
const commonAllergies = [
  "kacang tanah",
  "kacang pokok",
  "makanan laut (kerang, udang, ketam)",
  "ikan",
  "telur",
  "susu",
  "soya",
  "gandum"
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

    <div class="space-y-2">
      <h3 class="text-xl font-semibold">Ada sebarang keperluan diet?</h3>
      <span class="block text-slate-500">Pilih semua yang berkaitan</span>
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
    </div>

    <div class="space-y-2">
      <h3 class="text-xl font-semibold">
        Ada sebarang alahan atau bahan yang ingin dielakkan?
      </h3>
      <div class="flex items-center gap-2">
        <FormInput
          id="allergy"
          v-model="allergy"
          class="flex-grow"
          placeholder="Taip alahan atau bahan yang ingin dielakkan..."
        />
        <Button
          variant="primary-outline"
          icon="plus"
        >
          Tambah
        </Button>
      </div>
      <div class="space-y-2">
        <span class="block text-slate-500">Alergi biasa:</span>
        <ul class="flex flex-wrap gap-1">
          <li
            v-for="allergy in commonAllergies"
            :key="allergy"
            class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
          >
            {{ capitalizeFirstLetter(allergy) }}
          </li>
        </ul>
      </div>
    </div>
    
    <div class="space-y-2">
      <h3 class="text-xl font-semibold">Masakan mana yang ada gemari?</h3>
      <span class="block text-slate-500">Pilih semua yang berkaitan</span>
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
    </div>

    <div class="space-y-2">
      <h3 class="text-xl font-semibold">Sejauh mana tahap kepedasan yang anda suka?</h3>
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
    </div>

    <div class="flex justify-end">
      <Button icon="floppy-disk">
        Simpan Citarasa
      </Button>
    </div>
  </div>
</template>