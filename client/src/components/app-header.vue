<script setup lang="ts">
import Button from './button.vue';
</script>

<template>
  <header class="border-b">
    <div class="max-w-7xl mx-auto p-3 flex justify-between">
      <div>Dapur AI</div>
      <Button variant="primary-outline">
        <font-awesome-icon :icon="['fas', 'arrow-right-to-bracket']" />
        <span>Sign In</span>
      </Button>
    </div>
  </header>
</template>