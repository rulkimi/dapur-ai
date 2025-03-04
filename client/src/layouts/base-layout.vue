<script setup lang="ts">
import AppHeader from '../components/app-header.vue';
</script>

<template>
  <AppHeader />
  <div class="max-w-7xl mx-auto p-3">
    <slot></slot>
  </div>
</template>