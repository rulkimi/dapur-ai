<script setup lang="ts">
import { useStepperStore } from "../../stores/singup/signup-stepper-store";
import { ref, watch, computed } from "vue";

export interface Step {
  id: string;
  title: string;
}

const props = defineProps<{
  currentStep: number;
  steps: Step[];
}>();

const previousStep = ref<number>(0);

watch(
  () => props.currentStep,
  (_, oldStep) => {
    previousStep.value = oldStep;
    console.log(transitionName.value)
  }
);

const transitionName = computed(() => {
  return props.currentStep > previousStep.value ? "next" : "prev";
});

const emit = defineEmits<{
  (e: "update:currentStep", step: number): void;
}>();

const stepperStore = useStepperStore();
const handleClick = (index: number) => {
  console.log(stepperStore.completedSteps, index + 1);
  if (stepperStore.completedSteps.includes(index)) {
    // Check if step is completed
    emit("update:currentStep", index + 1);
  }
};
</script>

<template>
  <div class="space-y-6 mx-auto max-w-3xl">
    <ul class="flex gap-2 justify-between">
      <li
        v-for="(step, index) in steps"
        :key="index"
        class="flex-grow cursor-pointer"
        :class="[
          currentStep >= index + 1 ? 'text-teal-500' : 'text-slate-500',
          !stepperStore.completedSteps.includes(index + 1) &&
          index + 1 > currentStep
            ? 'cursor-not-allowed'
            : '',
        ]"
        @click="handleClick(index)"
      >
        <div
          class="h-1 rounded-full mb-1"
          :class="currentStep >= index + 1 ? 'bg-teal-500' : 'bg-gray-200'"
        ></div>
        <span>{{ step.title }}</span>
      </li>
    </ul>
    <div v-for="(step, index) in steps" :key="index">
      <transition :name="transitionName" mode="out-in">
        <div v-show="index + 1 === currentStep">
          <slot :name="step.id"></slot>
        </div>
      </transition>
    </div>
    <div class="flex gap-1">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<style scoped>
.next-enter-active,
.next-leave-active {
  transition: all 0.5s ease;
  position: absolute;
}
.next-enter-from {
  opacity: 0;
  transform: translateX(100%);
}
.next-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

.prev-enter-active,
.prev-leave-active {
  transition: all 0.5s ease;
  position: absolute;
}
.prev-enter-from {
  opacity: 0;
  transform: translateX(-100%);
}
.prev-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
