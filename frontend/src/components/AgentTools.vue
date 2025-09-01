<template>
  <div class="mb-3 last:mb-0">
    <div
      class="flex items-center gap-1.5 mb-1.5 font-semibold text-xs text-gray-500 uppercase tracking-wider"
    >
      <span class="text-sm">🛠️</span>
      <span class="text-gray-500">{{ agent.tool_name }}</span>
    </div>
    <div
      class="text-sm leading-relaxed text-gray-700  font-mono text-xs text-green-600 bg-green-50 px-2.5 py-1.5 rounded-md mt-1 border border-green-200 break-words whitespace-pre-wrap"
    >
      {{ agent.tool_result }}
      
    </div>
  </div>
</template>
<script setup lang="ts">
import { defineProps } from "vue";
import type { Agent } from "../types";

const props = defineProps<{
  agent: Agent;
}>();
</script>

<style lang="less" scoped></style>
