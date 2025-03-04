<script setup lang="ts">
import Button from './button.vue';
</script>

<template>
  <footer class="px-6 py-24 bg-teal-50 space-y-4 flex flex-col items-center">
    <div class="text-center mx-auto space-y-3">
      <span class="block text-3xl font-semibold">Cari Resipi Kegemaran Anda?</span>
      <span class="block text-xl text-slate-500 max-w-xl">
        Sertai komuniti kami dan temui ratusan resipi yang disesuaikan dengan bahan yang tersedia.
      </span>
    </div>
    <Button size="lg" icon="magnifying-glass">Cari Resipi</Button>
  </footer>
</template>