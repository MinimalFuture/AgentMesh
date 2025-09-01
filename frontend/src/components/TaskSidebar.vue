<template>
  <div class="w-70 bg-white/95 backdrop-blur-md border-r border-white/20 flex flex-col transition-all duration-300 ease-out shadow-lg" :class="{ 'collapsed': isCollapsed }">
    <div class="flex items-center px-5 py-4 border-b border-black/10 gap-3 h-14 flex-shrink-0 bg-white/95">
      <button 
        class="bg-white/80 border border-black/8 cursor-pointer p-2.5 rounded-xl text-gray-500 transition-all duration-200 ease-in-out flex items-center justify-center backdrop-blur-md hover:bg-white hover:text-gray-700 hover:-translate-y-0.5 hover:shadow-lg" 
        @click="$emit('toggle')"
        title="Collapse Task List"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h3 class="text-base font-semibold text-gray-700 m-0">Task List</h3>
    </div>
    
    <div class="p-4 overflow-y-auto">
      <div v-if="tasks.length === 0" class="text-center py-16 px-5 text-gray-400">
        <p class="mb-2 text-sm">No tasks yet</p>
        <p class="text-xs opacity-70">Tasks will appear here after you start a conversation</p>
      </div>
      <div v-else>
        <div 
          v-for="task in tasks" 
          :key="task.id"
          class="flex gap-2.5 p-3 rounded-lg mb-1.5 bg-white/90 border border-black/8 transition-all duration-200 ease-in-out cursor-pointer min-h-15 hover:bg-white hover:border-black/12"
          :class="{ 
            'bg-white border-primary-500 shadow-[0_0_0_1px_rgba(51,112,255,0.2)]': task.status === 'running', 
            'bg-white/80 opacity-80': task.status === 'completed' 
          }"
        >
          <div class="flex-shrink-0 pt-1">
            <div class="w-2 h-2 rounded-full bg-gray-300 flex-shrink-0" :class="{ 'bg-gray-500 animate-pulse': task.status === 'running', 'bg-gray-400': task.status === 'completed' }"></div>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-sm font-semibold text-gray-700 mb-0.5 leading-tight line-clamp-1">{{ task.title }}</h4>
            <p class="text-xs text-gray-500 leading-tight line-clamp-1">{{ task.description }}</p>
            <div class="flex justify-between items-center text-xs text-gray-400 mt-1">
              <span class="task-time">{{ formatTime(task.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, withDefaults } from 'vue'
import type { Task, TaskSidebarProps, TaskSidebarEmits } from '../types'

const props = withDefaults(defineProps<TaskSidebarProps>(), {
  isCollapsed: false,
  tasks: () => []
})

const emit = defineEmits<TaskSidebarEmits>()

const formatTime = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<style scoped>
/* Custom scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Collapsed state */
.w-70.collapsed {
  width: 0;
  border-right: 0;
  overflow: hidden;
}

/* Responsive */
@media (max-width: 768px) {
  .w-70 {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .w-70:not(.collapsed) {
    transform: translateX(0);
  }

  .w-70.collapsed {
    width: 0;
    transform: translateX(-100%);
  }
}
</style> 