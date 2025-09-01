import type { AgentSection, Tool } from "../types";
import { AGENT_EVENT_TYPES } from "../types/agentSection";
// /**
//  * Create a new agent section
//  */
// export function createAgentSection(
//   type: AgentSection['type'],
//   data: any,
//   order: number,
//   id?: string
// ): AgentSection {
//   return {
//     id: id || `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
//     type,
//     data,
//     order
//   };
// }

// /**
//  * Build sections array from legacy agent properties
//  */
// export function buildSectionsFromLegacy(agent: Agent): AgentSection[] {
//   const sections: AgentSection[] = [];
//   let order = 0;

//   if (agent.task) {
//     sections.push(createAgentSection('task', agent.task, order++));
//   }

//   if (agent.thinking) {
//     sections.push(createAgentSection('thinking', agent.thinking, order++));
//   }

//   if (agent.tools && agent.tools.length > 0) {
//     sections.push(createAgentSection('tools', agent.tools, order++));
//   }

//   if (agent.response) {
//     sections.push(createAgentSection('result', agent.response, order++));
//   }

//   return sections;
// }

// /**
//  * Add a section to an agent
//  */
// export function addSectionToAgent(
//   agent: Agent,
//   type: AgentSection['type'],
//   data: any,
//   order?: number
// ): Agent {
//   const sections = agent.sections || [];
//   const newOrder = order ?? Math.max(...sections.map(s => s.order), -1) + 1;

//   const newSection = createAgentSection(type, data, newOrder);

//   return {
//     ...agent,
//     sections: [...sections, newSection]
//   };
// }

// /**
//  * Update a section in an agent
//  */
// export function updateSectionInAgent(
//   agent: Agent,
//   sectionId: string,
//   updates: Partial<AgentSection>
// ): Agent {
//   if (!agent.sections) return agent;

//   const sections = agent.sections.map(section =>
//     section.id === sectionId ? { ...section, ...updates } : section
//   );

//   return {
//     ...agent,
//     sections
//   };
// }

// /**
//  * Remove a section from an agent
//  */
// export function removeSectionFromAgent(agent: Agent, sectionId: string): Agent {
//   if (!agent.sections) return agent;

//   const sections = agent.sections.filter(section => section.id !== sectionId);

//   return {
//     ...agent,
//     sections
//   };
// }

// /**
//  * Reorder sections in an agent
//  */
// export function reorderSections(agent: Agent, sectionIds: string[]): Agent {
//   if (!agent.sections) return agent;

//   const sections = agent.sections.map(section => {
//     const newOrder = sectionIds.indexOf(section.id);
//     return newOrder >= 0 ? { ...section, order: newOrder } : section;
//   });

//   return {
//     ...agent,
//     sections
//   };
// }

export function handleAgentSection(data: any, agentMessages: any): any {
  switch (data.event) {
    case AGENT_EVENT_TYPES.USER_TASK_SUBMIT:
      return handleUserTaskSubmit(data, agentMessages);
    case AGENT_EVENT_TYPES.AGENT_DECISION:
      return handleAgentDecision(data, agentMessages);
    case AGENT_EVENT_TYPES.AGENT_THINKING:
      return handleAgentThinking(data, agentMessages);
    case AGENT_EVENT_TYPES.TOOL_DECISION:
      return handleToolDecision(data, agentMessages);
    case AGENT_EVENT_TYPES.TOOL_EXECUTE:
      return handleToolExecute(data, agentMessages);
    case AGENT_EVENT_TYPES.AGENT_RESULT:
      return handleAgentResult(data, agentMessages);
    // case AGENT_EVENT_TYPES.TASK_RESULT:
    //   return handleTaskResult(data, agentMessages);
    default:
      return agentMessages;
  }
}
function handleUserTaskSubmit(data: any, agentMessages: any): Array<any> {
  // if (agentMessages.length === 0) {
  //   agentMessages.push(data);
  // }
  return agentMessages;
}
function handleAgentDecision(data: any, agentMessages: any): Array<any> {
  const list = agentMessages;
  const newData = data.data;
  list.push({
    task_id: newData.task_id,
    agent_id: newData.agent_id,
    agent_name: newData.agent_name,
    agent_avatar: newData.agent_avatar,
    sub_task: newData.sub_task,
    timestamp: new Date().toISOString(),
    type: "agent_decision",
  });
  return list;
  // return {
  //   event: "agent_decision",
  //   data: {
  //     ...data,
  //   },
  // };
}

function handleAgentThinking(data: any, agentMessages: any): AgentSection {
  const newData = data.data;
  const index = agentMessages.findIndex(
    (item: any) => item.agent_id === newData.agent_id
  );
  if (index !== -1) {
    agentMessages[index] = {
      ...agentMessages[index],
      thought: newData.thought + agentMessages[index].thought,
    };
  }
  const list = agentMessages;
  return list;
}

function handleToolDecision(data: any, agentMessages: any): AgentSection {
  const list = agentMessages;
  const newData = data.data;
  const index = list.findIndex((item: any) => {
    return item.agent_id === newData.agent_id;
  });
  // console.log("list", index);
  if (index !== -1) {
    // Initialize tools array if it doesn't exist
    if (!list[index].tools) {
      list[index].tools = [];
    }

    const toolsIndex = list[index].tools.findIndex(
      (item: any) => item.tool_name === newData.tool_name
    );
    if (toolsIndex !== -1) {
      list[index]["tools"][toolsIndex] = {
        ...newData,
        type: "tool",
        toolsLoading: false,
      };
    } else {
      list[index]["tools"].push({
        ...newData,
        toolsLoading: true,
      });
    }
  }
  return list;
}

function handleToolExecute(data: any, agentMessages: any): AgentSection {
  const list = agentMessages;
  const newData = data.data;
  const index = list.findIndex(
    (item: any) => item.agent_id === newData.agent_id
  );

  if (index !== -1) {
    // Initialize tools array if it doesn't exist
    if (!list[index].tools) {
      list[index].tools = [];
    }

    const toolsIndex = list[index].tools.findIndex(
      (item: any) => item.tool_name === newData.tool_name
    );
    if (toolsIndex !== -1) {
      list[index]["tools"][toolsIndex] = {
        ...newData,
        type: "tool",
        toolsLoading: false,
      };
    } else {
      list[index]["tools"].push({
        ...newData,
        toolsLoading: true,
      });
    }
  }
  return list;
}

function handleAgentResult(data: any, agentMessages: any): AgentSection {
  const list = agentMessages;
  const newData = data.data;
  const index = list.findIndex(
    (item: any) => item.agent_id === newData.agent_id
  );
  if (index !== -1) {
    list[index] = {
      ...list[index],
      ...newData,
    };
  }
  console.log("list", list);
  return list;
}

function handleTaskResult(data: any): AgentSection {
  return {
    event: "task_result",
    data: {
      ...data,
      timestamp: new Date().toISOString(),
      type: "task_completion",
      status: "finished",
      completionTime: Date.now(),
    },
  };
}
