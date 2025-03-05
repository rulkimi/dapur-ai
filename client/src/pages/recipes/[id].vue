<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import HeadingTitle from '../../components/heading-title.vue';
const route = useRoute();
const recipeId = route.params.id;

const recipes = ref<string[]>([])
console.log(recipeId);
</script>

<template>
  <div>
    <HeadingTitle 
      title="Resipi untuk Anda"
      :subtitle="`Kami jumpa ${recipes.length} resipi yang anda boleh buat dengan bahan yang ada.`"
    />
  </div>
</template>