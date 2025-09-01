// Common types for the application

export interface Task {
  id: number;
  title: string;
  description: string;
  agent: string;
  status: "pending" | "running" | "completed" | "failed";
  timestamp: Date;
}

export interface Message {
  id: number;
  type: "user" | "system" | "agent";
  sender: string;
  content: string;
  timestamp: Date;
}

export interface Tool {
  id: string;
  name: string;
  params: string;
}

export interface Agent {
  task_id: string;
  agent_id: string;
  agent_name: string;
  agent_avatar: string;
  sub_task?: string;
  thought?: string;
  timestamp: string;
  type?: string;
}

// Re-export AgentSection types from dedicated file
export * from "./agentSection";

export interface AgentLog {
  id: number;
  type: "info" | "warning" | "error";
  timestamp: Date;
  message: string;
}

export interface ActiveTool {
  id: string;
  name: string;
  icon: string;
  data: {
    type: "search" | "terminal" | "file";
    query?: string;
    command?: string;
    path?: string;
    content?: string;
    output?: string;
    results?: Array<{
      id: number;
      title: string;
      snippet: string;
      url: string;
    }>;
  };
}

export interface ExamplePrompt {
  text: string;
  category?: string;
}

// Component props interfaces with default values
export interface TaskSidebarProps {
  isCollapsed?: boolean;
  tasks?: Task[];
}

export interface FloatingToggleButtonProps {
  isCollapsed?: boolean;
}

export interface AgentMessageProps {
  agent: any;
}

export interface AgentProcessPanelProps {
  isAgentRunning?: boolean;
  agentMessages?: Agent[];
}

export interface ChatInputProps {
  inputMessage?: string;
  isLoading?: boolean;
}

export interface SplitViewProps {
  isAgentRunning?: boolean;
  agentMessages?: Agent[];
  activeTools?: ActiveTool[];
  selectedTool?: string | null;
  inputMessage?: string;
  isLoading?: boolean;
}

export interface ToolResultsPanelProps {
  activeTools?: ActiveTool[];
  selectedTool?: string | null;
}

export interface WelcomeSectionProps {
  inputMessage?: string;
  isLoading?: boolean;
  examplePrompts?: string[];
}

// Event interfaces
export interface ChatInputEmits {
  "update:inputMessage": [value: string];
  send: [];
}

export interface WelcomeSectionEmits {
  "update:inputMessage": [value: string];
  send: [];
  setInputValue: [value: string];
}

export interface SplitViewEmits {
  "update:inputMessage": [value: string];
  send: [];
  selectTool: [toolId: string];
}

export interface ToolResultsPanelEmits {
  selectTool: [toolId: string];
}

export interface TaskSidebarEmits {
  toggle: [];
}

export interface FloatingToggleButtonEmits {
  toggle: [];
}
