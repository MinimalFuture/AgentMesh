<template>
  <MarkdownRenderer :content="agent.response" />
</template>
<script setup lang="ts">
import { defineProps } from "vue";
import type { Agent } from "../types";

const props = defineProps<{
  agent: Agent;
}>();
</script>

<style lang="less" scoped></style>
