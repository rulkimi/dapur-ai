<script setup lang="ts">
import { ref } from 'vue';
import Button from '../components/button.vue';
import Stepper, { type Step } from '../components/stepper.vue';
import FoodPreferences from '../components/signup/food-preferences.vue';

const steps: Step[] = [
  { title: 'Maklumat Akaun' },
  { title: 'Citarasa Makanan' },
  { title: 'Cipta Akaun' }
]
const currentStep = ref<number>(1);
const handlePreviousStep = () => {
  if (currentStep.value === 1) return;
  currentStep.value--
}
const handleNextStep = () => {
  if (currentStep.value === steps.length) return;
  currentStep.value++
}
</script>

<template>
  <Stepper
    :current-step="currentStep"
    :steps="steps"
  >
    <template #content="{ step }">
      <div v-if="step.title === 'Maklumat Akaun'">
        asdasd
      </div>
      <div v-else-if="step.title === 'Citarasa Makanan'">
        <FoodPreferences>
          <template #footer-button>
            <Button variant="primary-outline" @click="handlePreviousStep">Previous</Button>
          </template>
        </FoodPreferences>
      </div>
    </template>
    <template v-if="currentStep !== 2" #footer>
      <Button variant="primary-outline" @click="handlePreviousStep">Previous</Button>
      <Button @click="handleNextStep">Next</Button>
    </template>
  </Stepper>
</template>