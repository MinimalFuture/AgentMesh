import type { Agent } from '../types';
import { 
  createAgentSection, 
  addSectionToAgent, 
  buildSectionsFromLegacy 
} from '../utils/agentUtils';

// Example 1: Creating an agent with sections array
export const createAgentWithSections = (): Agent => {
  const agent: Agent = {
    id: 1,
    name: "Assistant",
    avatar: "/path/to/avatar.png",
    timestamp: new Date(),
    sections: [
      createAgentSection('task', 'Help user with their question', 0),
      createAgentSection('thinking', 'I need to analyze the user\'s request carefully', 1),
      createAgentSection('tools', [
        { id: 'tool1', name: 'Google Search', params: 'query: "example search"' }
      ], 2),
      createAgentSection('result', 'Here is the answer to your question...', 3)
    ]
  };

  return agent;
};

// Example 2: Adding sections dynamically
export const addSectionsDynamically = (agent: Agent): Agent => {
  let updatedAgent = agent;

  // Add a thinking section
  updatedAgent = addSectionToAgent(updatedAgent, 'thinking', 'Processing the request...');

  // Add a tools section
  updatedAgent = addSectionToAgent(updatedAgent, 'tools', [
    { id: 'tool2', name: 'Calculator', params: '2 + 2' }
  ]);

  // Add a result section
  updatedAgent = addSectionToAgent(updatedAgent, 'result', 'The calculation result is 4');

  return updatedAgent;
};

// Example 3: Converting legacy agent to new format
export const convertLegacyAgent = (legacyAgent: Agent): Agent => {
  const sections = buildSectionsFromLegacy(legacyAgent);
  
  return {
    ...legacyAgent,
    sections
  };
};

// Example 4: Complex agent with multiple sections
export const createComplexAgent = (): Agent => {
  const agent: Agent = {
    id: 2,
    name: "Research Assistant",
    avatar: "/path/to/research-avatar.png",
    timestamp: new Date(),
    sections: [
      createAgentSection('task', 'Research the latest AI developments', 0),
      createAgentSection('thinking', 'I should search for recent papers and news articles', 1),
      createAgentSection('tools', [
        { id: 'search1', name: 'Google Scholar', params: 'query: "AI developments 2024"' },
        { id: 'search2', name: 'ArXiv', params: 'query: "artificial intelligence recent papers"' }
      ], 2),
      createAgentSection('thinking', 'Found several relevant sources, now analyzing...', 3),
      createAgentSection('result', `
# AI Developments Summary

## Key Findings:
1. **Large Language Models**: Continued advancement in transformer architectures
2. **Multimodal AI**: Integration of text, image, and audio processing
3. **AI Ethics**: Growing focus on responsible AI development

## Sources:
- Recent papers from top AI conferences
- Industry reports and news articles
      `, 4)
    ]
  };

  return agent;
}; 