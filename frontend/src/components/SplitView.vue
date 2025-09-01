<template>
  <div class="flex-[1_0_0] flex gap-px bg-gray-200 overflow-hidden min-h-0" ref="messagesContainer">
    <!-- Left Panel: Agent Process and Input -->
    <div class="flex-[1_0_0] flex flex-col bg-white/95 backdrop-blur-md border-l border-black/10 min-h-0 min-w-0">
      <!-- Agent Process Panel -->
      <AgentProcessPanel 
        :is-agent-running="isAgentRunning"
        :agent-messages="agentMessages"
      />

      <!-- Input Area for conversation mode -->
      <ChatInput 
        :input-message="inputMessage"
        :is-loading="isLoading"
        @update:input-message="$emit('update:inputMessage', $event)"
        @send="$emit('send')"
      />
    </div>

    <!-- Right Panel: Tool Results (Full Height) -->
    <ToolResultsPanel 
      :active-tools="activeTools"
      :selected-tool="selectedTool"
      @select-tool="$emit('selectTool', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, withDefaults } from 'vue'
import AgentProcessPanel from './AgentProcessPanel.vue'
import ToolResultsPanel from './ToolResultsPanel.vue'
import ChatInput from './ChatInput.vue'
import type { SplitViewProps, SplitViewEmits } from '../types'

const props = withDefaults(defineProps<SplitViewProps>(), {
  isAgentRunning: false,
  agentMessages: () => [],
  activeTools: () => [],
  selectedTool: null,
  inputMessage: '',
  isLoading: false
})

const emit = defineEmits<SplitViewEmits>()
</script>

<style scoped>
/* Responsive */
@media (max-width: 768px) {
  .flex-\[1_0_0\] {
    flex-direction: column;
  }

  .flex-\[1_0_0\] > div:first-child {
    flex: 1;
  }
}
</style> 