<script setup lang="ts">
import Button from "../button.vue";
import { computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const isAuthenticated = computed(() => localStorage.getItem("authenticated"));

const goToSearchPage = () => {
  if (isAuthenticated.value) router.push("/recipes");
  else router.push("/login");
};
</script>

<template>
  <section class="flex flex-col md:flex-row items-center gap-12 md:my-32">
    <div class="space-y-6 md:w-1/2">
      <div class="space-y-2">
        <h1 class="text-4xl font-semibold">
          Resipi Sesuai Dengan Apa Yang Anda Ada
        </h1>
        <span class="block text-xl max-w-lg text-slate-500">
          Cari idea makanan yang sedap menggunakan bahan-bahan yang anda sedia
          ada di dapur anda.
        </span>
      </div>
      <div class="flex gap-2">
        <Button
          class="shadow-lg hover:shadow-sm"
          size="lg"
          icon="magnifying-glass"
          @click="goToSearchPage"
        >
          Cari Resipi
        </Button>
        <Button v-if="isAuthenticated" variant="primary-outline" size="lg">
          Kongsi ke Rakan
        </Button>
        <Button
          v-else
          variant="primary-outline"
          size="lg"
          @click="router.push('/recipes')"
        >
          Cuba Tanpa Log Masuk
        </Button>
      </div>
    </div>
    <div class="md:w-1/2">
      <img
        class="object-cover rounded-3xl"
        src="../../assets/hero-image.webp"
        alt="family having meals"
      />
    </div>
  </section>
</template>
