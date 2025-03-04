<script setup lang="ts">
import AppFooter from '../components/app-footer.vue';
import AppHeader from '../components/app-header.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <template v-if="route.path !== '/auth'">
    <AppHeader />
    <div class="max-w-7xl mx-auto p-6">
      <slot></slot>
    </div>
  </template>
  <template v-else>
    <div class="min-h-screen flex items-center justify-center">
      <slot></slot>
    </div>
  </template>
  <AppFooter v-if="route.path === '/'"/>
</template>