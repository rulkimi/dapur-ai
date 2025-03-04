<script setup lang="ts">
import Button from '../button.vue'
</script>

<template>
  <section class="flex items-center gap-2 my-24">
    <div class="space-y-6">
      <div class="space-y-2">
        <h1 class="text-5xl font-semibold">Find Perfect Recipes With What You Have</h1>
        <span class="block max-w-lg">Discover delicious meal ideas using ingredients you already have in your kitchen.</span>
      </div>
      <Button size="lg" icon="magnifying-glass">Get Started</Button>
    </div>
    <div class="w-1/2">
      <img
        class="object-cover rounded-3xl"
        src="../../assets/hero-image.webp"
        alt="family having meals"
      />
    </div>
  </section>
</template>