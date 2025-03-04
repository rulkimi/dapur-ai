<script setup lang="ts">
import HeroText from './hero-text.vue';
</script>

<template>
  <section class="flex items-center gap-2 my-24">
    <HeroText class="w-1/2" />
    <div class="w-1/2">
      <img
        class="object-cover rounded-3xl"
        src="../../assets/hero-image.webp"
        alt="family having meals"
      />
    </div>
  </section>
</template>