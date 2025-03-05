<script setup lang="ts">
import Button from '../components/button.vue';
import PreferenceLayout from '../layouts/preference-layout.vue';
import Allergies from '../components/preferences/allergies.vue';
import DietaryRestrictions from '../components/preferences/dietary-restrictions.vue';
import PreferredCuisines from '../components/preferences/preferred-cuisines.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { capitalizeFirstLetter } from '../utils';

const dietaryRestrictions = ref<string[]>([]);
const preferredCuisines = ref<string[]>([]);
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

const router = useRouter()
const savePreferences = () => {
  const food_preferences = {
    dietary_restrictions: dietaryRestrictions.value,
    allergies: allergies.value,
    preferred_cuisines: preferredCuisines.value,
    spice_level: preferredSpice.value
  }
  console.table(food_preferences)
  router.push('/ingredients')
}
</script>

<template>
  <div class="custom-card space-y-6 max-w-3xl mx-auto">
    <div class="text-center">
      <h2 class="text-2xl font-semibold">Kongsikan citarasa anda dengan kami</h2>
      <span class="block text-slate-500">Kami akan cadangkan resipi yang sesuai dengan selara anda</span>
    </div>

    <form @submit.prevent="savePreferences" class="space-y-6">
      <PreferenceLayout
        title="Ada sebarang keperluan diet?"
        subtitle="Pilih semua yang berkaitan"
      >
        <DietaryRestrictions v-model="dietaryRestrictions" />
      </PreferenceLayout>

      <PreferenceLayout title="Ada sebarang alahan atau bahan yang ingin dielakkan?">
        <Allergies v-model="allergies" />
      </PreferenceLayout>
      
      <PreferenceLayout
        title="Masakan mana yang ada gemari?"
        subtitle="Pilih semua yang berkaitan"
      >
        <PreferredCuisines v-model="preferredCuisines" />
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