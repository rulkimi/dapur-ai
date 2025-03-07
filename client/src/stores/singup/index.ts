import { defineStore } from "pinia"
import { type AccountInfo } from "../../components/signup/account-information.vue"
import { type FoodPreferences } from "../../components/signup/food-preferences.vue"

export const useSignupStore = defineStore('signup', {
  state: () => ({ 
    accountInfo: null as AccountInfo | null,
    foodPreferences: null as FoodPreferences | null
  }),
  getters: {
    // double: (state) => state.count * 2,
  },
  actions: {
    setAccountinfo(info: AccountInfo) {
      this.accountInfo = info;
    },
    setFoodPreferences(preferences: FoodPreferences) {
      this.foodPreferences = preferences;
    }
  },
})