<script setup lang="ts">
import AppFooter from "../components/app-footer.vue";
import AppHeader from "../components/app-header.vue";
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <AppHeader v-if="route.path !== '/login' && route.path !== '/signup'" />
  <div
    :class="
      route.path !== '/login'
        ? 'max-w-7xl mx-auto p-6'
        : 'min-h-screen flex items-center justify-center'
    "
  >
    <slot></slot>
  </div>
  <AppFooter v-if="route.path === '/'" />
</template>
