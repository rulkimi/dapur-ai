<script setup lang="ts">
import AppFooter from '../components/app-footer.vue';
import AppHeader from '../components/app-header.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <AppHeader />
  <div class="max-w-7xl mx-auto p-6">
    <slot></slot>
  </div>
  <AppFooter v-if="route.path === '/'"/>
</template>