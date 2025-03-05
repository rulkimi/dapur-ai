<script setup lang="ts">
import FormInput from '../components/form-input.vue';
import Button from '../components/button.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter()

const email = ref<string>('')
const password = ref<string>('')

const logIn = () => {
  console.log('login')
  router.push('/preferences')
}
</script>

<template>
  <div class="custom-card bg-white max-w-md mx-auto space-y-5">
    <font-awesome-icon class="text-teal-500 text-6xl mx-auto block" :icon="['fas', 'kitchen-set']" />
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
        />
        <FormInput
          id="password"
          type="password"
          v-model="password"
          icon="lock"
          placeholder="・・・・・・・"
          label="Password"
        />
      </div>
      <div class="space-y-2">
        <Button
          width="full"
          icon="arrow-right-to-bracket"
          type="submit"
        >
          Log masuk
        </Button>
        <Button
          width="full"
          variant="primary-outline"
          icon="home"
          @click="router.push('/')"
        >
          Back Home
        </Button>
      </div>
    </form>
    <p class="block text-slate-500 text-center">
      Tiada akaun? <a href="" class="text-teal-500 hover:underline">Daftar sekarang</a>
    </p>
  </div>
</template>