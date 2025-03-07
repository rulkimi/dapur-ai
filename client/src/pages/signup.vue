<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import Button from "../components/button.vue";
import SignupStepper, {
  type Step,
} from "../components/signup/signup-stepper.vue";
import FoodPreferences from "../components/signup/food-preferences.vue";
import AccountInformation from "../components/signup/account-information.vue";
import { useStepperStore } from "../stores/singup/signup-stepper-store";
import { useSignupStore } from "../stores/singup";
import FoodPreferencesReadonly from "../components/signup/food-preferences-readonly.vue";

onBeforeMount(() => document.title = 'Cipta Akaun - DapurAI')

const steps: Step[] = [
  { id: "info", title: "Maklumat Akaun" },
  { id: "preferences", title: "Citarasa Makanan" },
  { id: "create", title: "Cipta Akaun" },
];

const stepperStore = useStepperStore();
const signupStore = useSignupStore()
const currentStep = ref<number>(stepperStore.currentStep);

const handlePreviousStep = () => {
  if (currentStep.value === 1) return;
  stepperStore.setCurrentStep(currentStep.value--);
};
const handleNextStep = () => {
  console.table(signupStore.accountInfo)
  console.table(signupStore.foodPreferences)
  if (currentStep.value === steps.length) return;
  // completedSteps.value.push(currentStep.value);
  stepperStore.setCompletedSteps(currentStep.value);
  stepperStore.setCurrentStep(currentStep.value++);
  console.log(stepperStore.completedSteps);
};
const handleStepChange = (step: number) => {
  currentStep.value = step;
};
</script>

<template>
  <SignupStepper
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
      <FoodPreferences @next="handleNextStep">
        <template #footer-button>
          <Button variant="primary-outline" @click="handlePreviousStep">Sebelum</Button>
        </template>
      </FoodPreferences>
    </template>
    <template #create>
      <AccountInformation
        v-if="stepperStore.currentStep === 2"
        readonly
      />
      <FoodPreferencesReadonly
        v-if="signupStore.foodPreferences"
        :preferences="signupStore.foodPreferences" 
      />
      <div class="flex justify-end gap-1 py-4">
        <Button variant="primary-outline" @click="handlePreviousStep">Sebelum</Button>
        <Button>Cipta Akaun</Button>
      </div>
    </template>
  </SignupStepper>
</template>
