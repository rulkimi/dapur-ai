<script setup lang="ts">
import FormInput from '../form-input.vue';
import Button from '../button.vue';
import { capitalizeFirstLetter } from '../../utils'
import { ref } from 'vue';
const props = defineProps<{
  modelValue: string[]
}>()

const emit = defineEmits(['update:modelValue'])

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
const allergy = ref<string>('')

const handleEnterKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && allergy.value.trim() !== '') addAllergy(allergy.value);
}
const addAllergy = (newAllergy: string) => {
  if (props.modelValue.includes(newAllergy)) {
    allergy.value = ''
    return
  }
  emit('update:modelValue', [...props.modelValue, newAllergy])
  allergy.value = ''
}
const removeAllergy = (index: number) => {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index));
}
</script>

<template>
  <div class="flex items-center gap-2">
    <FormInput
      id="allergy"
      v-model="allergy"
      class="flex-grow"
      placeholder="Taip alahan atau bahan yang ingin dielakkan..."
      @keyup.enter="handleEnterKeydown"
    />
    <Button
      variant="primary-outline"
      icon="plus"
      @click="addAllergy(allergy)"
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
        @click="addAllergy(allergy)"
      >
        {{ capitalizeFirstLetter(allergy) }}
      </li>
    </ul>
    <span v-if="modelValue.length" class="block text-slate-500">Alergi anda:</span>
    <ul class="flex flex-wrap gap-1">
      <li
        v-for="(allergy, index) in modelValue"
        :key="allergy"
        class="bg-gray-100 hover:bg-gray-200 cursor-pointer text-slate-600 rounded-md px-2 py-0.5"
      >
        {{ capitalizeFirstLetter(allergy) }}
        <font-awesome-icon
          class="hover:scale-110 hover:text-slate-800 transition-all duration-300"
          :icon="['fas', 'times']"
          @click="removeAllergy(index)"
        />
      </li>
    </ul>
  </div>
</template>