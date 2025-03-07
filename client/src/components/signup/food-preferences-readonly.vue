<script setup lang="ts">
import { type FoodPreferences } from './food-preferences.vue';
import PreferenceLayout from '../../layouts/preference-layout.vue';
import Allergies from "./preferences/allergies.vue";
import DietaryRestrictions from "./preferences/dietary-restrictions.vue";
import PreferredCuisines from "./preferences/preferred-cuisines.vue";
import { capitalizeFirstLetter } from '../../utils';

defineProps<{
  preferences: FoodPreferences
}>()
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <PreferenceLayout
      title="Keperluan Diet"
    >
      <DietaryRestrictions readonly v-model="preferences.dietary_restrictions" />
    </PreferenceLayout>

    <PreferenceLayout
      title="Alahan"
    >
      <Allergies readonly v-model="preferences.allergies" />
    </PreferenceLayout>

    <PreferenceLayout
      title="Masakan Kegemaran"
    >
      <PreferredCuisines readonly v-model="preferences.preferred_cuisines" />
    </PreferenceLayout>

    <PreferenceLayout title="Tahap Kepedasan">
      <span class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5">
        {{ capitalizeFirstLetter(preferences.preferred_spice) }}
      </span>
    </PreferenceLayout>
  </div>
</template>