<script setup lang="ts">
import FormInput from '../form-input.vue';
import { ref } from 'vue';

const username = ref<string>('')
const birthDate = ref<string>('')
const email = ref<string>('')
const password = ref<string>('')
</script>

<template>
  <div class="space-y-4">
    <div class="md:grid md:grid-cols-5 gap-2 border-b py-8 space-y-2 md:space-y-0">
      <div class="col-span-2 font-semibold text-xl">Maklumat Akaun</div>
      <div class="col-span-3 space-y-2">
        <div class="flex flex-col md:flex-row gap-2">
          <FormInput
            class="flex-grow"
            v-model="username"
            id="username"
            label="Nama pengguna"
            placeholder="johndoe"
            icon="user"
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
            v-model="email"
            id="email"
            label="E-mel"
            placeholder="johndoe@mail.com"
            icon="envelope"
          />
          <FormInput
            v-model="password"
            id="password"
            type="password"
            label="Kata laluan"
            placeholder="********"
            icon="lock"
          />
        </div>
      </div>
    </div>
    <div class="flex justify-end gap-1">
      <slot name="footer"></slot>
    </div>
  </div>
</template>