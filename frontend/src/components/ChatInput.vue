<template>
  <div class="px-5 py-4 border-t border-black/10 bg-gray-50/50 flex-shrink-0">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-end bg-white/95 border border-white/30 rounded-2xl px-5 py-4 backdrop-blur-xl shadow-lg transition-all duration-300 ease-in-out min-h-14">
        <textarea
          :value="inputMessage"
          @input="(event) => $emit('update:inputMessage', (event.target as HTMLTextAreaElement).value)"
          @keydown="handleKeyDown"
          placeholder="Enter your task"
          class="flex-1 border-none outline-none resize-none text-base leading-relaxed font-inherit min-h-6 max-h-30 bg-transparent text-gray-700 min-h-10 pt-2 pb-2"
          rows="1"
          ref="chatInput"
        ></textarea>
        <div class="flex items-end gap-2 ml-3 self-end">
          <button class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500" title="Upload File">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49"/>
            </svg>
          </button>
          <button class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500" title="Voice Input">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <path d="M12 19v3"/>
            </svg>
          </button>
          <button class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500" title="More Options">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="1"/>
              <circle cx="19" cy="12" r="1"/>
              <circle cx="5" cy="12" r="1"/>
            </svg>
          </button>
          <button 
            @click="$emit('send')"
            :disabled="!inputMessage.trim() || isLoading"
            class="bg-gradient-to-br from-primary-500 to-primary-800 text-white border-none rounded-xl p-2.5 cursor-pointer transition-all duration-300 ease-in-out flex items-center justify-center min-w-10 h-10 shadow-lg hover:from-primary-800 hover:to-primary-900 hover:-translate-y-0.5 hover:shadow-xl disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
          >
            <svg v-if="!isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 2L11 13"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
            </svg>
            <div v-else class="w-4 h-4 border-2 border-transparent border-t-white rounded-full animate-spin"></div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, withDefaults } from 'vue'
import type { ChatInputProps, ChatInputEmits } from '../types'

const props = withDefaults(defineProps<ChatInputProps>(), {
  inputMessage: '',
  isLoading: false
})

const emit = defineEmits<ChatInputEmits>()

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    emit('send')
  }
}
</script>

<style scoped>
/* Focus styles */
.backdrop-blur-xl:focus-within {
  @apply border-primary-500 shadow-xl -translate-y-0.5;
}

/* Placeholder styles */
textarea::placeholder {
  @apply text-gray-400 text-start leading-relaxed;
}
</style> 