<script setup lang="ts">
import { onBeforeMount } from 'vue';
import HeroSection from '../components/home/hero-section.vue';
import WhyDapurai from '../components/home/why-dapurai.vue';

onBeforeMount(() => document.title = 'DapurAI')
</script>

<template>
  <div>
    <HeroSection />
    <WhyDapurai />
  </div>
</template>