<template>
  <div
    class="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 font-sans overflow-hidden"
  >
    <!-- Navigation -->

    <!-- Main Content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Floating Toggle Button -->
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
      <div
        class="flex-1 flex flex-col transition-all duration-300 ease-in-out relative"
        :class="{ 'ml-0': isTaskListCollapsed }"
      >
        <div class="flex-1 flex flex-col relative">
          <!-- Split View for Agent Process and Tool Results -->
          <SplitView
            :is-agent-running="isAgentRunning"
            :agent-messages="agentMessages"
            :active-tools="activeTools"
            :selected-tool="selectedTool"
            :input-message="inputMessage"
            :is-loading="isLoading"
            @update:input-message="inputMessage = $event"
            @send="sendMessage"
            @select-tool="selectedTool = $event"
          />

          <!-- Welcome Section with centered input -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import productAvatar from "../assets/images/product.png";
import developerAvatar from "../assets/images/developer.png";
import type { Message, Task, Agent, AgentLog, ActiveTool } from "../types";

// Import components
import FloatingToggleButton from "../components/FloatingToggleButton.vue";
import TaskSidebar from "../components/TaskSidebar.vue";

import SplitView from "../components/SplitView.vue";
import { handleAgentSection } from "../utils/agentUtils";
const route = useRoute();

// Reactive data
const isTaskListCollapsed = ref<boolean>(true);
const inputMessage = ref<string>("");
const isLoading = ref<boolean>(false);
const messages = ref<Message[]>([]);
const tasks = ref<Task[]>([]);
const isAgentRunning = ref<boolean>(false);
const selectedTool = ref<string | null>(null);
const agentLogs = ref<AgentLog[]>([]);
const activeTools = ref<ActiveTool[]>([]);
const agentMessages = ref<any[]>([]);

// Watch for route changes to handle initial message
watch(
  () => route.query.message,
  (newMessage) => {
    if (newMessage && typeof newMessage === "string") {
      inputMessage.value = newMessage;
      // Auto-send the message if it comes from route
      nextTick(() => {
        sendMessage();
      });
    }
  },
  { immediate: true }
);

// Methods
const toggleTaskList = (): void => {
  isTaskListCollapsed.value = !isTaskListCollapsed.value;
};

const sendMessage = async (): Promise<void> => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userMessage: Message = {
    id: Date.now(),
    type: "user",
    sender: "You",
    content: inputMessage.value.trim(),
    timestamp: new Date(),
  };

  messages.value.push(userMessage);

  const newTask: Task = {
    id: Date.now(),
    title:
      inputMessage.value.substring(0, 50) +
      (inputMessage.value.length > 50 ? "..." : ""),
    description: inputMessage.value,
    agent: "Task Coordinator",
    status: "running",
    timestamp: new Date(),
  };

  tasks.value.unshift(newTask);

  const userInput = inputMessage.value;
  inputMessage.value = "";
  isLoading.value = true;
  isAgentRunning.value = true;

  if (messages.value.length === 1) {
    isTaskListCollapsed.value = false;
  }

  initializeMockData();

  setTimeout(() => {
    const systemMessage: Message = {
      id: Date.now() + 1,
      type: "system",
      sender: "AgentMesh",
      content: `I have received your request: "${userInput}". The agent team is analyzing your task and will start processing soon. You can monitor the progress in the task list on the left.`,
      timestamp: new Date(),
    };

    messages.value.push(systemMessage);
    isLoading.value = false;

    setTimeout(() => {
      newTask.status = "completed";
      isAgentRunning.value = false;
    }, 5000);
  }, 1000);
};
const data1: any = {
  event: "user_task_submit",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:10.718984",
  data: {
    status: "success",
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    msg: "Task submitted successfully",
  },
};
const data2: any = {
  event: "agent_decision",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.441255",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    agent_name: "General Agent",
    agent_avatar: "",
    sub_task: "Please tell me today's date and time",
  },
};
const data3: any = {
  event: "tool_decision",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.444163",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_id: "time",
    tool_name: "time",
    thought:
      "用户想要了解当前的日期和时间。为了确保信息准确，需要调用time工具获取本地当前时间。",
    parameters: {
      format: "human",
      timezone: "local",
    },
  },
};
const data4: any = {
  event: "tool_execute",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.446606",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_name: "time",
    status: "success",
    execution_time: 0,
    tool_result: {
      current_time: "2025-07-31 10:31:08",
      components: {
        year: 2025,
        month: 7,
        day: 31,
        hour: 10,
        minute: 31,
        second: 8,
        weekday: "Thursday",
      },
      format: "human",
      timezone: "local",
    },
  },
};
const data5: any = {
  event: "tool_decision",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.448629",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_id: "file_save",
    tool_name: "file_save",
    thought: null,
    parameters: {},
  },
};

const data6: any = {
  event: "tool_execute",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.450435",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_name: "file_save",
    status: "success",
    execution_time: 0,
    tool_result: {
      status: "success",
      file_path:
        "workspace\\general_team\\current_date_and_time\\current_datetime_message.txt",
    },
  },
};

const data7: any = {
  event: "tool_decision",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.451797",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_id: "file_save",
    tool_name: "file_save",
    thought: null,
    parameters: {},
  },
};

const data8: any = {
  event: "tool_execute",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.452800",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_name: "file_save",
    status: "success",
    execution_time: 0,
    tool_result: {
      status: "success",
      file_path:
        "workspace\\general_team\\current_date_and_time\\current_datetime_message.txt",
    },
  },
};

const data9: any = {
  event: "tool_decision",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.453374",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_id: "file_save",
    tool_name: "file_save",
    thought: null,
    parameters: {},
  },
};

const data10: any = {
  event: "tool_execute",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.454650",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    agent_id: "General Agent",
    tool_name: "file_save",
    status: "success",
    execution_time: 0,
    tool_result: {
      status: "success",
      file_path:
        "workspace\\general_team\\current_date_and_time\\current_datetime_message.txt",
    },
  },
};

const data11: any = {
  event: "agent_result",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.456013",
  data: {
    agent_id: "General Agent",
    result:
      "Today's date and time are: Friday, August 1, 2025, at 10:52:13 AM (local time). If you require the time in other time zones or more detailed information, please feel free to let me know!",
  },
};

const data12: any = {
  event: "task_result",
  task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
  timestamp: "2025-08-01T10:52:16.458619",
  data: {
    task_id: "62e60329-3df9-40b6-88ca-b2468eaf38e5",
    status: "success",
  },
};

const mockData = (): void => {
  setTimeout(() => {
    agentMessages.value = handleAgentSection(data1, agentMessages.value);
    setTimeout(() => {
      agentMessages.value = handleAgentSection(data2, agentMessages.value);
      setTimeout(() => {
        agentMessages.value = handleAgentSection(data3, agentMessages.value);
        setTimeout(() => {
          agentMessages.value = handleAgentSection(data4, agentMessages.value);
          setTimeout(() => {
            agentMessages.value = handleAgentSection(
              data5,
              agentMessages.value
            );
            setTimeout(() => {
              agentMessages.value = handleAgentSection(
                data6,
                agentMessages.value
              );

              setTimeout(() => {
                agentMessages.value = handleAgentSection(
                  data7,
                  agentMessages.value
                );
                setTimeout(() => {
                  agentMessages.value = handleAgentSection(
                    data8,
                    agentMessages.value
                  );
                  setTimeout(() => {
                    agentMessages.value = handleAgentSection(
                      data9,
                      agentMessages.value
                    );

                    setTimeout(() => {
                      agentMessages.value = handleAgentSection(
                        data10,
                        agentMessages.value
                      );
                      setTimeout(() => {
                        agentMessages.value = handleAgentSection(
                          data11,
                          agentMessages.value
                        );
                        setTimeout(() => {
                          agentMessages.value = handleAgentSection(
                            data12,
                            agentMessages.value
                          );
                        }, 2000);
                      }, 2000);
                    }, 2000);
                  }, 2000);
                }, 2000);
              }, 2000);
            }, 2000);
          }, 2000);
        }, 2000);
      }, 2000);
    }, 2000);
  }, 2000);
};

const initializeMockData = (): void => {
  mockData();
  agentLogs.value = [
    {
      id: 1,
      type: "info",
      timestamp: new Date(),
      message:
        "Team Super Assistant Team received the task and started processing",
    },
  ];


  activeTools.value = [
    {
      id: "search1",
      name: "Web Search",
      icon: "🔍",
      data: {
        type: "search",
        query: "AgentMesh multi-agent framework 2025",
        results: [
          {
            id: 1,
            title:
              "AgentMesh 2.0 Release - Advanced Multi-Agent Orchestration Framework",
            snippet:
              "AgentMesh platform released version 2.0 on January 15, 2025, featuring enhanced agent communication protocols, distributed task execution, and intelligent workflow coordination...",
            url: "https://github.com/MinimalFuture/AgentMesh",
          },
          {
            id: 2,
            title:
              "AgentMesh Documentation - Getting Started with Multi-Agent Systems",
            snippet:
              "Comprehensive guide to building and deploying multi-agent systems using AgentMesh framework, including team configuration, task distribution, and real-time monitoring...",
            url: "https://github.com/MinimalFuture/AgentMesh",
          },
          {
            id: 3,
            title: "AgentMesh Tool Ecosystem - Extensible Agent Capabilities",
            snippet:
              "The latest version includes a rich ecosystem of tools for agent interaction, including web browsing, file operations, search capabilities, and custom tool integration...",
            url: "https://github.com/MinimalFuture/AgentMesh",
          },
        ],
      },
    },
  ];

  selectedTool.value = "search1";

  tasks.value = [
    {
      id: 1,
      title: "AgentMesh Framework Research and Analysis",
      description:
        'I will use search tools to retrieve "AgentMesh" related information, including framework capabilities, multi-agent features, etc.',
      agent: "Research Agent",
      status: "completed",
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: 2,
      title: "Multi-Agent System Configuration",
      description:
        "I am configuring the agent team structure and defining communication protocols for optimal task execution.",
      agent: "System Agent",
      status: "running",
      timestamp: new Date(Date.now() - 120000),
    },
    {
      id: 3,
      title: "AgentMesh Documentation Review",
      description:
        "I will review the AgentMesh documentation to understand best practices for agent coordination.",
      agent: "Documentation Agent",
      status: "pending",
      timestamp: new Date(Date.now() - 60000),
    },
    {
      id: 4,
      title: "Agent Performance Monitoring Setup",
      description:
        "I will set up real-time monitoring for agent performance and task execution metrics.",
      agent: "Monitoring Agent",
      status: "pending",
      timestamp: new Date(),
    },
  ];
};

onMounted(() => {
  const textarea = document.querySelector(".chat-input") as HTMLTextAreaElement;
  if (textarea) {
    textarea.addEventListener("input", () => {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    });
  }
});
</script>

<style scoped>
/* Responsive */
@media (max-width: 768px) {
  .flex-1 {
    margin-left: 0;
  }
}
</style>
