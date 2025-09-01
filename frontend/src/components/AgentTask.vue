<template>
  <div
    class="flex items-center gap-1.5 mb-1.5 font-semibold text-xs text-gray-500 uppercase tracking-wider"
  >
    <span class="text-sm">📋</span>
    <span class="text-gray-500">Task Received</span>
  </div>
  <div class="text-sm leading-relaxed text-gray-700 ml-5">{{ agent.task }}</div>
</template>
<script lang="ts" setup>
import { defineProps } from "vue";
import type { Agent } from "../types";

const props = defineProps<{
  agent: Agent;
}>();
</script>

<style lang="less" scoped></style>
