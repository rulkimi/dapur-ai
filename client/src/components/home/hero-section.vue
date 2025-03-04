<script setup lang="ts">
import Button from '../button.vue'
</script>

<template>
  <section class="flex flex-col md:flex-row items-center gap-12 md:my-32">
    <div class="space-y-6 md:w-1/2">
      <div class="space-y-2">
        <h1 class="text-4xl font-semibold">Resipi Sesuai Dengan Apa Yang Anda Ada</h1>
        <span class="block text-xl max-w-lg text-slate-500">Cari idea makanan yang sedap menggunakan bahan-bahan yang anda sudah ada di dapur.</span>
      </div>
      <Button size="lg" icon="magnifying-glass">Cari Resipi</Button>
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