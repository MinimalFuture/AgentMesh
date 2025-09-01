<template>
  <div class="flex gap-3 mb-5">
    <div class="flex-shrink-0">
      <img
        :src="agent.agent_avatar"
        :alt="agent.agent_name"
        class="w-10 h-10 rounded-full border-2 border-white/80 shadow-lg"
      />
    </div>
    <div class="flex-1 min-w-0">
      <div
        class="bg-white/95 border border-black/8 rounded-xl p-4 shadow-lg backdrop-blur-md"
      >
        <div
          class="flex items-center justify-between mb-4 pb-2 border-b border-black/5"
        >
          <span class="text-sm font-semibold text-gray-700">{{
            agent.agent_name
          }}</span>
          <span class="text-xs text-gray-400">{{
            formatLogTime(agent.timestamp)
          }}</span>
        </div>
        <div>
          <!-- Use sections array if available, otherwise fallback to legacy structure -->
          <template v-if="sortedSections && sortedSections.length > 0">
            <AgentSection
              v-for="(section, index) in sortedSections"
              :key="index"
              :section="section"
            />
          </template>
        </div>
        <div>
          <MarkdownRenderer :content="agent.result" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch } from "vue";
import type { AgentMessageProps } from "../types";

import AgentSection from "./AgentSection.vue";
import MarkdownRenderer from "./MarkdownRenderer.vue";

const props = defineProps<AgentMessageProps>();

// const sortedSections = computed(() => {
//   console.log("props.agent", props.agent);
//   if (!props.agent.sections) return [];
//   // return [...props.agent.sections].sort((a, b) => a.order - b.order);
//   return props.agent;
// });
const sortedSections = ref<any[]>([]);
watch(props.agent, (newVal) => {
  sortedSections.value = newVal.tools;
});
const formatLogTime = (date: Date | string): string => {
  console.log("date", date);
  const dateObj = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(dateObj);
};
</script>

<style scoped>
/* Component specific styles */
</style>
