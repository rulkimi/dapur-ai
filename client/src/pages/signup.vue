<script setup lang="ts">
import { ref } from 'vue';
import Button from '../components/button.vue';
import Stepper, { type Step } from '../components/stepper.vue';
import FoodPreferences from '../components/signup/food-preferences.vue';
import AccountInformation from '../components/signup/account-information.vue';

const steps: Step[] = [
  { id: 'info', title: 'Maklumat Akaun' },
  { id: 'preferences', title: 'Citarasa Makanan' },
  { id: 'create', title: 'Cipta Akaun' }
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
const handleStepChange = (step: number) => {
  currentStep.value = step;
}
</script>

<template>
  <Stepper
    :current-step="currentStep"
    :steps="steps"
    @update:currentStep="handleStepChange"
  >
    <template #info>
      <AccountInformation @next="handleNextStep">
        <template #footer>
          <div class="flex gap-1">
            <Button variant="primary-outline" @click="handlePreviousStep">Previous</Button>
          </div>
        </template>
      </AccountInformation>
    </template>
    <template #preferences>
      <FoodPreferences>
        <template #footer-button>
          <Button variant="primary-outline" @click="handlePreviousStep">Previous</Button>
        </template>
      </FoodPreferences>
    </template>
  </Stepper>
</template>