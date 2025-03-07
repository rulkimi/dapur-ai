<script setup lang="ts">
import FormInput from '../components/form-input.vue';
import Button from '../components/button.vue';
import { computed, onBeforeMount, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';

onBeforeMount(() => document.title = 'Log Masuk - DapurAI')
const router = useRouter()

const email = ref<string>('')
const password = ref<string>('')
const loading = ref<boolean>(false)

const rules = computed(() => ({
  email: { required },
  password: { required }
}))

const v$ = useVuelidate(rules, { email,  password })

const logIn = async () => {
  await v$.value.$validate()
  loading.value = true
  try {
    setTimeout(() => router.push('/recipes'), 3000)
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <div class="custom-card bg-white max-w-md mx-auto space-y-5">
    <!-- <font-awesome-icon class="text-teal-500 text-6xl mx-auto block" :icon="['fas', 'kitchen-set']" /> -->
     <img src="/logo.svg" class="size-24 mx-auto block" alt="DapurAI Brand Logo">
    <div class="text-center mx-auto space-y-2">
      <span class="block text-3xl font-semibold">DapurAI</span>
      <span class="block text-slate-500">Cari resipi yang sedap dengan bahan-bahan yang anda ada di dapur</span>
    </div>
    <form class="space-y-4" @submit.prevent="logIn">
      <div class="space-y-2">
        <FormInput
          id="email"
          v-model="email"
          icon="envelope"
          placeholder="johndoe@mail.com"
          label="Email"
          :error="v$.email.$error"
          :error-message="v$.email.$error ? 'Sila masukkan E-mel' : ''"
        />
        <FormInput
          id="password"
          type="password"
          v-model="password"
          icon="lock"
          placeholder="・・・・・・・"
          label="Password"
          :error="v$.password.$error"
          :error-message="v$.password.$error ? 'Sila masukkan kata laluan' : ''"
        />
      </div>
      <div class="space-y-2">
        <Button
          width="full"
          icon="arrow-right-to-bracket"
          type="submit"
          :loading="loading"
        >
          Log masuk
        </Button>
        <Button
          width="full"
          variant="primary-outline"
          icon="home"
          @click="router.push('/')"
          :disabled="loading"
        >
          Back Home
        </Button>
      </div>
    </form>
    <p class="block text-slate-500 text-center">
      Tiada akaun?
      <Button
        variant="link"
        @click="router.push('/signup')"
        :disabled="loading"
      >
        Daftar sekarang
      </Button>
    </p>
  </div>
</template>