<script setup lang="ts">
import Button from './button.vue';
</script>

<template>
  <header class="sticky bg-white backdrop-filter backdrop-blur-sm bg-opacity-80 top-0 border-b">
    <div class="max-w-7xl mx-auto py-3 px-6 flex items-center justify-between">
      <div class="text-teal-500 font-semibold flex items-center gap-2">
        <font-awesome-icon :icon="['fas', 'kitchen-set']" />
        Dapur AI
      </div>
      <Button variant="primary-outline" icon="arrow-right-to-bracket">
        Log masuk
      </Button>
    </div>
  </header>
</template>