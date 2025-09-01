<template>
  <div class="flex-1 flex flex-col min-h-0">
    <div
      class="px-5 py-4 border-b border-black/10 flex items-center justify-between bg-white/95 h-14 flex-shrink-0"
    >
      <h3 class="text-sm font-semibold text-gray-700 m-0">Agent Process</h3>
      <div class="flex items-center gap-2">
        <span
          class="w-2 h-2 rounded-full bg-gray-300 transition-all duration-300 ease-in-out"
          :class="{
            'bg-primary-500 animate-pulse shadow-[0_0_0_4px_rgba(51,112,255,0.3)]':
              isAgentRunning,
          }"
        ></span>
        <span class="text-xs text-gray-500 font-medium">{{
          isAgentRunning ? "Running" : "Completed"
        }}</span>
      </div>
    </div>
    <div
      class="flex-[1_0_0] overflow-y-auto overflow-x-hidden px-5 py-4 flex flex-col gap-5 min-h-0"
    >
      <AgentMessage
        v-for="agent in agentMessages"
        :key="agent.task_id"
        :agent="agent"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, withDefaults } from "vue";
import AgentMessage from "./AgentMessage.vue";
import type { AgentProcessPanelProps } from "../types";

const props = withDefaults(defineProps<AgentProcessPanelProps>(), {
  isAgentRunning: false,
  agentMessages: () => [],
});
</script>

<style scoped>
/* Custom scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>
