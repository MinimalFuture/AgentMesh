/**
 * AgentSection Type Definitions
 * 
 * This file contains all type definitions related to AgentSection, including:
 * - Event type constants
 * - Data interface definitions
 * - Mapping types
 * - Generic interfaces
 * - Type guard functions
 * - Utility functions
 * 
 * Design Philosophy:
 * 1. Centralized management of all event types
 * 2. Use mapping types to associate events with data
 * 3. Generics provide type safety
 * 4. Auto-generate related types and functions
 * 5. Easy to extend and maintain
 */

// Event type definitions - Centralized management of all event types
export const AGENT_EVENT_TYPES = {
  USER_TASK_SUBMIT: "user_task_submit",
  AGENT_DECISION: "agent_decision",
  AGENT_THINKING: "agent_thinking", 
  TOOL_DECISION: "tool_decision",
  TOOL_EXECUTE: "tool_execute",
  AGENT_RESULT: "agent_result",
  TASK_RESULT: "task_result"
} as const;

// Event type union
export type AgentEventType = typeof AGENT_EVENT_TYPES[keyof typeof AGENT_EVENT_TYPES];

export interface UserTaskSubmitData {
  task_id: string;
  status: string;
  msg: string;
}

// Basic data type definitions
export interface AgentDecisionData {
  task_id: string;
  agent_id: string;
  agent_name: string;
  agent_avatar: string;
  sub_task: string;
}

export interface AgentThinkingData {
  task_id: string;
  agent_id: string;
  thought: string;
}

export interface ToolDecisionData {
  task_id: string;
  agent_id: string;
  tool_id: string;
  tool_name: string;
  thought: string;
  parameters: Record<string, any>;
}

export interface ToolExecuteData {
  task_id: string;
  agent_id: string;
  tool_name: string;
  status: string;
  execution_time: number;
  tool_result: any;
}

export interface AgentResultData {
  agent_id: string;
  result: string;
}

export interface TaskResultData {
  task_id: string;
  status: string;
}

// Event data mapping type - Automatically associate event types with data interfaces
export interface AgentEventDataMap {
  [AGENT_EVENT_TYPES.USER_TASK_SUBMIT]: UserTaskSubmitData;
  [AGENT_EVENT_TYPES.AGENT_DECISION]: AgentDecisionData;
  [AGENT_EVENT_TYPES.AGENT_THINKING]: AgentThinkingData;
  [AGENT_EVENT_TYPES.TOOL_DECISION]: ToolDecisionData;
  [AGENT_EVENT_TYPES.TOOL_EXECUTE]: ToolExecuteData;
  [AGENT_EVENT_TYPES.AGENT_RESULT]: AgentResultData;
  [AGENT_EVENT_TYPES.TASK_RESULT]: TaskResultData;
}

// Generic AgentSection interface - Use generics to provide type safety
export interface AgentSection<T extends AgentEventType = AgentEventType> {
  event: T;
  data: AgentEventDataMap[T];
}

// Specific event interfaces - Auto-generated, no manual maintenance required
export type UserTaskSubmitSection = AgentSection<typeof AGENT_EVENT_TYPES.USER_TASK_SUBMIT>;
export type AgentDecisionSection = AgentSection<typeof AGENT_EVENT_TYPES.AGENT_DECISION>;
export type AgentThinkingSection = AgentSection<typeof AGENT_EVENT_TYPES.AGENT_THINKING>;
export type ToolDecisionSection = AgentSection<typeof AGENT_EVENT_TYPES.TOOL_DECISION>;
export type ToolExecuteSection = AgentSection<typeof AGENT_EVENT_TYPES.TOOL_EXECUTE>;
export type AgentResultSection = AgentSection<typeof AGENT_EVENT_TYPES.AGENT_RESULT>;
export type TaskResultSection = AgentSection<typeof AGENT_EVENT_TYPES.TASK_RESULT>;

// Union of all specific event types - Auto-generated
export type SpecificAgentSection = 
  | UserTaskSubmitSection
  | AgentDecisionSection
  | AgentThinkingSection
  | ToolDecisionSection
  | ToolExecuteSection
  | AgentResultSection
  | TaskResultSection;

// Type guard function generator - Auto-generate type guards for each event type
export function createEventTypeGuard<T extends AgentEventType>(eventType: T) {
  return (section: AgentSection): section is AgentSection<T> => {
    return section.event === eventType;
  };
}

// Predefined type guard functions
export const isUserTaskSubmitSection = createEventTypeGuard(AGENT_EVENT_TYPES.USER_TASK_SUBMIT);
export const isAgentDecisionSection = createEventTypeGuard(AGENT_EVENT_TYPES.AGENT_DECISION);
export const isAgentThinkingSection = createEventTypeGuard(AGENT_EVENT_TYPES.AGENT_THINKING);
export const isToolDecisionSection = createEventTypeGuard(AGENT_EVENT_TYPES.TOOL_DECISION);
export const isToolExecuteSection = createEventTypeGuard(AGENT_EVENT_TYPES.TOOL_EXECUTE);
export const isAgentResultSection = createEventTypeGuard(AGENT_EVENT_TYPES.AGENT_RESULT);
export const isTaskResultSection = createEventTypeGuard(AGENT_EVENT_TYPES.TASK_RESULT);

// Event creator - Provide type-safe creation functions
export function createAgentSection<T extends AgentEventType>(
  event: T,
  data: AgentEventDataMap[T]
): AgentSection<T> {
  return { event, data };
} 