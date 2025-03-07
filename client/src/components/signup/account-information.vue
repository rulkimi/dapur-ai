<script setup lang="ts">
import FormInput from '../form-input.vue';
import Button from '../button.vue';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { useSignupStore } from '../../stores/singup';

export interface AccountInfo {
  username: string
  birthDate?: string
  email: string
  password: string
  confirmPassword: string
}

const router = useRouter()
const signupStore = useSignupStore()

const username = ref<string>('')
const birthDate = ref<string>('')
const email = ref<string>('')
const password = ref<string>('')
const confirmPassword = ref<string>('')

const showPassword = ref<boolean>(false)
const showConfirmPassword = ref<boolean>(false)

const rules = computed(() => ({
  username: { required },
  email: { required },
  password: { required },
  confirmPassword: { required }
}))

const v$ = useVuelidate(rules, {
  username,
  email,
  password,
  confirmPassword
})

const error = ref<boolean>(false)
const errorMessage = ref<string>('')

const isPasswordMatch = () => {
  return password.value === confirmPassword.value; 
};

const emit = defineEmits(['next', 'step-completed']) 

const handleNextButtonClick = async () => {
  await v$.value.$validate()
  if (!isPasswordMatch()) {
    error.value = true
    errorMessage.value = 'Passwords do not match.'
    return
  } else if (!v$.value.$error) { 
    signupStore.setAccountinfo({
      username: username.value,
      email: email.value,
      birthDate: birthDate.value,
      password: password.value,
      confirmPassword: confirmPassword.value
    })
    emit('next')
    emit('step-completed')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="md:grid md:grid-cols-5 gap-2 border-b py-8 space-y-2 md:space-y-0">
      <div class="col-span-2 font-semibold text-xl">Maklumat Akaun</div>
      <div class="col-span-3 space-y-2">
        <div class="flex flex-col md:flex-row gap-2">
          <FormInput
            required
            class="flex-grow"
            v-model="username"
            id="username"
            label="Nama pengguna"
            placeholder="johndoe"
            icon="user"
            :error="v$.username.$error"
            :error-message="v$.username.$error ? 'Nama pengguna diperlukan' : ''"
          />
          <FormInput
            class="flex-grow"
            v-model="birthDate"
            id="birth-date"
            label="Tarikh lahir"
            placeholder="20 Dec 1999"
            icon="calendar-alt"
          />
        </div>
        <div class="space-y-2">
          <FormInput
            required
            v-model="email"
            id="email"
            label="E-mel"
            placeholder="johndoe@mail.com"
            icon="envelope"
            :error="v$.email.$error"
            :error-message="v$.email.$error ? 'Emel diperlukan' : ''"
          />
          <FormInput
            required
            v-model="password"
            id="password"
            :type="showPassword ? 'text' : 'password'"
            label="Kata laluan"
            placeholder="********"
            icon="lock"
            @input="error = false; errorMessage = ''"
            :error="error || v$.password.$error"
            :error-message="v$.password.$error ? 'Sila masukkan kata laluan' : errorMessage"
          >
            <template #append-icon>
              <font-awesome-icon
                class="hover:scale-110 cursor-pointer transition-transform duration-300"
                :icon="['fas', showPassword ? 'eye-slash' : 'eye']"
                @click="showPassword = !showPassword"
              />
            </template>
          </FormInput>
          <FormInput
            required
            v-model="confirmPassword"
            id="confirm-password"
            :type="showConfirmPassword ? 'text' : 'password'"
            label="Sahkan Kata Laluan"
            placeholder="********"
            icon="lock"
            @input="error = false; errorMessage = ''"
            :error="error || v$.confirmPassword.$error"
            :error-message="v$.confirmPassword.$error ? 'Sila sahkan kata laluan' : errorMessage"
          >
          <template #append-icon>
              <font-awesome-icon
                class="hover:scale-110 cursor-pointer transition-transform duration-300"
                :icon="['fas', showConfirmPassword ? 'eye-slash' : 'eye']"
                @click="showConfirmPassword = !showConfirmPassword"
              />
            </template>
          </FormInput>
        </div>
      </div>
    </div>
    <div class="flex justify-between gap-1">
      <Button variant="link" @click="router.go(-1)">Back</Button>
      <Button @click="handleNextButtonClick">Next</Button>
    </div>
  </div>
</template>