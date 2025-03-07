<script setup lang="ts">
import Button from "./button.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const goToSearchPage = () => {
  const isAuthenticated = localStorage.getItem("authenticated");
  if (isAuthenticated) router.push("/recipes");
  else router.push("/login");
};
</script>

<template>
  <footer class="px-6 py-24 bg-teal-50 space-y-4 flex flex-col items-center">
    <!-- <font-awesome-icon
      class="text-teal-500 text-6xl"
      :icon="['fas', 'kitchen-set']"
    /> -->
    <img src="/logo.svg" class="size-24" alt="DapurAI Brand Logo" />
    <div class="text-center mx-auto space-y-3">
      <span class="block text-3xl font-semibold">Nak Cari Resipi Mudah?</span>
      <span class="block text-xl text-slate-500 max-w-xl">
        Sertai komuniti kami dan temui ratusan resipi yang disesuaikan dengan
        bahan yang tersedia.
      </span>
    </div>
    <Button size="lg" icon="magnifying-glass" @click="goToSearchPage"
      >Cari Resipi</Button
    >
  </footer>
</template>
