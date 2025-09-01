<template>
  <button 
    v-if="isCollapsed"
    class="fixed top-5 left-5 z-[1001] bg-white/90 text-gray-500 border border-white/30 rounded-xl p-3 cursor-pointer transition-all duration-300 ease-in-out flex items-center justify-center shadow-lg backdrop-blur-md hover:bg-white hover:text-gray-700 hover:-translate-y-0.5 hover:shadow-xl" 
    @click="$emit('toggle')"
    title="Expand Task List"
  >
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M3 12h18m-9-9l9 9-9 9"/>
    </svg>
  </button>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, withDefaults } from 'vue'
import type { FloatingToggleButtonProps, FloatingToggleButtonEmits } from '../types'

const props = withDefaults(defineProps<FloatingToggleButtonProps>(), {
  isCollapsed: true
})

const emit = defineEmits<FloatingToggleButtonEmits>()
</script> 