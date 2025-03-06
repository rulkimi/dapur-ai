import { defineStore } from "pinia"

export const useStepperStore = defineStore('counter', {
  state: () => ({ 
    currentStep: 1 as number,
    completedSteps: [0] as number[]
  }),
  getters: {
    // double: (state) => state.count * 2,
  },
  actions: {
    setCurrentStep(step: number) {
      this.currentStep = step;
    },
    setCompletedSteps(step: number) {
      this.completedSteps = [...this.completedSteps, step];
    }
  },
})