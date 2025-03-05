<script setup lang="ts">
import BaseLayout from './layouts/base-layout.vue';
</script>

<template>
  <BaseLayout>
    <router-view v-slot="{ Component }">
      <Transition name="fade">
        <component :is="Component"></component>
    </Transition>
    </router-view>
  </BaseLayout>
</template>

<style scoped>
.fade-enter-active {
  transition: transform 0.5s, opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-from {
  transform: translateY(20px);
}
.fade-leave-to {
  transform: translateY(-20px);
}
</style>