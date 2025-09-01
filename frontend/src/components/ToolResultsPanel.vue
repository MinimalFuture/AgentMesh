<template>
  <div class="flex-1 bg-white/95 backdrop-blur-md flex flex-col min-h-0">
    <div class="px-5 py-4 border-b border-black/10 flex items-center justify-between bg-white/95 h-14 flex-shrink-0">
      <h3 class="text-sm font-semibold text-gray-700 m-0">Tool Execution Results</h3>
      <div class="flex gap-1">
        <button 
          v-for="tool in activeTools" 
          :key="tool.id"
          class="flex items-center gap-1.5 px-3 py-2 bg-transparent border-none rounded-md cursor-pointer transition-all duration-200 ease-in-out text-xs text-gray-500 hover:bg-primary-500/10 hover:text-primary-500"
          :class="{ 'bg-primary-500 text-white': selectedTool === tool.id }"
          @click="$emit('selectTool', tool.id)"
        >
          <span class="text-sm">{{ tool.icon }}</span>
          <span class="font-medium">{{ tool.name }}</span>
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto overflow-x-hidden p-5 min-h-0 h-px">
      <div v-if="selectedToolData" class="tool-result">
        <div v-if="selectedToolData.type === 'search'" class="search-result">
          <h4 class="text-sm font-semibold text-gray-700 mb-3">Search Results</h4>
          <div class="text-xs text-gray-500 mb-4 px-3 py-2 bg-gray-100 rounded-md font-mono">Query: {{ selectedToolData.query }}</div>
          <div class="space-y-3">
            <div v-for="item in selectedToolData.results" :key="item.id" class="p-3 border border-gray-200 rounded-lg bg-gray-50/80">
              <h5 class="text-sm font-semibold text-gray-800 mb-1.5 leading-relaxed">{{ item.title }}</h5>
              <p class="text-sm text-gray-600 leading-relaxed mb-2">{{ item.snippet }}</p>
              <a :href="item.url" class="text-xs text-primary-500 no-underline break-all hover:underline" target="_blank">{{ item.url }}</a>
            </div>
          </div>
        </div>
        <div v-else-if="selectedToolData.type === 'terminal'" class="terminal-result">
          <h4 class="text-sm font-semibold text-gray-700 mb-3">Terminal Execution</h4>
          <div class="font-mono text-xs text-green-600 bg-green-50 px-3 py-2 rounded-md mb-3">$ {{ selectedToolData.command }}</div>
          <pre class="font-mono text-xs text-gray-700 bg-gray-50 p-3 rounded-md whitespace-pre-wrap overflow-x-auto">{{ selectedToolData.output }}</pre>
        </div>
        <div v-else-if="selectedToolData.type === 'file'" class="file-result">
          <h4 class="text-sm font-semibold text-gray-700 mb-3">File Content</h4>
          <div class="font-mono text-xs text-gray-500 bg-gray-100 px-3 py-2 rounded-md mb-3">{{ selectedToolData.path }}</div>
          <pre class="font-mono text-xs text-gray-700 bg-gray-50 p-3 rounded-md whitespace-pre-wrap overflow-x-auto border border-gray-200">{{ selectedToolData.content }}</pre>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-50 text-gray-400 text-sm">
        <p>Select a tool from the left to view execution results</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed, withDefaults } from 'vue'
import type { ToolResultsPanelProps, ToolResultsPanelEmits, ActiveTool } from '../types'

const props = withDefaults(defineProps<ToolResultsPanelProps>(), {
  activeTools: () => [],
  selectedTool: null
})

const emit = defineEmits<ToolResultsPanelEmits>()

const selectedToolData = computed(() => {
  if (!props.selectedTool) return null
  const tool = props.activeTools.find((t: ActiveTool) => t.id === props.selectedTool)
  return tool?.data || null
})
</script>

<style scoped>
/* Responsive */
@media (max-width: 768px) {
  .flex.gap-1 {
    flex-wrap: wrap;
  }
}
</style> 