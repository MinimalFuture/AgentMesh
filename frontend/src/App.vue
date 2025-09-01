<template>
  <div id="app">
    <LanguageSwitcher />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import LanguageSwitcher from './components/LanguageSwitcher.vue'
</script>
