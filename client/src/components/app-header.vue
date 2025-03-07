<script setup lang="ts">
import Button from "./button.vue";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <header
    class="sticky top-0 z-[10] bg-white backdrop-filter backdrop-blur-sm bg-opacity-80 border-b"
  >
    <div class="max-w-7xl mx-auto py-3 px-6 flex items-center justify-between">
      <div
        class="text-teal-500 text-xl font-semibold flex items-center gap-2 cursor-pointer group"
        @click="router.push('/')"
      >
        <!-- <font-awesome-icon
          class="group-hover:scale-110 transition-transform duration-300"
          :icon="['fas', 'kitchen-set']"
        /> -->
        <img src="/logo.svg" class="size-6" alt="DapurAI Brand Logo" />
        <span
          class="font-bold bg-clip-text text-transparent bg-gradient-to-t from-teal-600 to-teal-400"
        >
          DapurAI
        </span>
      </div>
      <Button
        variant="primary-outline"
        icon="arrow-right-to-bracket"
        @click="router.push('/login')"
      >
        Log masuk
      </Button>
    </div>
  </header>
</template>
