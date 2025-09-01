<template>
  <div class="language-switcher">
    <div class="relative">
      <button
        @click="isOpen = !isOpen"
        class="flex items-center gap-2 px-3 py-2 bg-white/80 border border-white/30 rounded-lg cursor-pointer transition-all duration-200 ease-in-out hover:bg-white/95 hover:-translate-y-0.5 hover:shadow-lg backdrop-blur-md"
        :title="currentLanguage === 'zh-CN' ? 'Switch to English' : '切换到中文'"
      >
        <span class="text-sm font-medium">{{ getCurrentLanguageName() }}</span>
        <svg 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
          :class="{ 'rotate-180': isOpen }"
          class="transition-transform duration-200"
        >
          <path d="M7 10l5 5 5-5"/>
        </svg>
      </button>
      
      <!-- Language Dropdown -->
      <div 
        v-if="isOpen" 
        class="absolute right-0 top-full mt-2 bg-white/95 border border-white/30 rounded-lg shadow-xl backdrop-blur-xl min-w-32 z-50"
      >
        <div class="py-1">
          <button
            v-for="locale in supportedLocales"
            :key="locale.code"
            @click="selectLanguage(locale.code)"
            class="w-full px-4 py-2 text-left text-sm hover:bg-primary-500/10 transition-colors duration-200 flex items-center gap-2"
            :class="{ 'bg-primary-500/20 text-primary-700': currentLanguage === locale.code }"
          >
            <span class="text-lg">{{ locale.flag }}</span>
            <span>{{ locale.name }}</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Backdrop to close dropdown -->
    <div 
      v-if="isOpen" 
      @click="isOpen = false"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLanguage, getSupportedLocales } from '../utils/i18n'
import type { Locale } from '../i18n'

const isOpen = ref(false)
const { locale, switchLanguage, initLanguage } = useLanguage()
const supportedLocales = getSupportedLocales()

const currentLanguage = computed(() => locale.value)

const getCurrentLanguageName = () => {
  const current = supportedLocales.find(l => l.code === currentLanguage.value)
  return current ? current.name : '中文'
}

const selectLanguage = (newLocale: Locale) => {
  switchLanguage(newLocale)
  isOpen.value = false
}

onMounted(() => {
  initLanguage()
})
</script>

<style scoped>
.language-switcher {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}
</style> 