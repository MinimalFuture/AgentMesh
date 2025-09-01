<template>
  <div>

    <!-- Task Section -->
    <div v-if="section.type === 'task'" class="mb-3 last:mb-0">
      <AgentTask :agent="section"></AgentTask>
    </div>

    <!-- Tools Section -->
    <div v-else-if="section.type === 'tool'" class="mb-3 last:mb-0">
      <AgentTools :agent="section"></AgentTools>
    </div>

    <!-- Result Section -->
    <div v-else-if="section.type === 'result'" class="mb-3 last:mb-0">
      <AgentResult :agent="section"></AgentResult>
    </div>

  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import type { AgentSection } from "../types";

import AgentTask from "./AgentTask.vue";
import AgentTools from "./AgentTools.vue";
import AgentResult from "./AgentResult.vue";
const props = defineProps<{
  section: AgentSection;
}>();
</script>

<style scoped>
/* Component specific styles */
</style>
