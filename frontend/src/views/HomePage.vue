<template>
  <div
    class="flex h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 font-sans overflow-hidden"
  >
    <FloatingToggleButton
      :is-collapsed="isTaskListCollapsed"
      @toggle="toggleTaskList"
    />

    <!-- Task List Sidebar -->
    <TaskSidebar
      :is-collapsed="isTaskListCollapsed"
      :tasks="tasks"
      @toggle="toggleTaskList"
    />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col relative">
      <div class="flex-1 flex flex-col relative">
        <!-- Welcome Section with centered input -->
        <WelcomeSection
          :input-message="inputMessage"
          :is-loading="isLoading"
          :example-prompts="examplePrompts"
          @update:input-message="inputMessage = $event"
          @send="handleSendMessage"
          @set-input-value="setInputValue"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import WelcomeSection from "../components/WelcomeSection.vue";
import FloatingToggleButton from "../components/FloatingToggleButton.vue";
import TaskSidebar from "../components/TaskSidebar.vue";
import type { Task } from "../types";
const router = useRouter();

// Reactive data
const isTaskListCollapsed = ref<boolean>(true);
const inputMessage = ref<string>("");
const isLoading = ref<boolean>(false);
const tasks = ref<Task[]>([]);
// Example prompts for users
const examplePrompts = [
  "Generate a comprehensive quarterly business performance report",
  "Create a Python web scraper for e-commerce product data",
  "Build a React dashboard with real-time analytics charts",
  "Generate a technical documentation report for API endpoints",
];

// Methods
const setInputValue = (value: string): void => {
  inputMessage.value = value;
  nextTick(() => {
    const chatInput = document.querySelector(
      ".chat-input"
    ) as HTMLTextAreaElement;
    if (chatInput) {
      chatInput.focus();
    }
  });
};

const handleSendMessage = async (): Promise<void> => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  // Navigate to chat page with the message
  router.push({
    name: "Chat",
    query: { message: inputMessage.value.trim() },
  });
};
const toggleTaskList = (): void => {
  isTaskListCollapsed.value = !isTaskListCollapsed.value;
};
</script>
