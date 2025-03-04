<script setup lang="ts">
import FeatureCard, { type Feature } from './feature-card.vue';

const features: Feature[] = [
  { 
    icon: 'magnifying-glass', 
    title: 'Cari Mengikut Bahan',
    description: 'Hanya masukkan bahan yang anda ada, dan kami akan mencadangkan resipi yang boleh anda buat dengan segera.'
  },
  {
    icon: 'clock',
    title: 'Resipi Cepat & Mudah',
    description: 'Cari resipi yang cepat disediakan, sesuai untuk waktu petang atau merancang makanan.'
  },
  {
    icon: 'utensils',
    title: 'Pilihan Bernutrisi',
    description: 'Cari makanan seimbang yang akan menjaga kesihatan dan kepuasan anda sekeluarga.'
  }
]
</script>

<template>
  <section class="space-y-8">
    <div class="max-w-2xl mx-auto space-y-2 text-center">
      <h2 class="text-4xl font-semibold">Kenapa DapurAI?</h2>
      <span class="block text-slate-500">
        Platform kami membantu anda menyediakan makanan berkhasiat dan memuaskan dengan usaha minimum.
      </span>
    </div>

    <ul class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <li
        v-for="feature in features"
        :key="feature.title"
        class="flex flex-col"
      >
        <FeatureCard :feature="feature" />
      </li>
    </ul>
  </section>
</template>