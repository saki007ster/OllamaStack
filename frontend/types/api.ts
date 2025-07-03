// API Request Types
export interface ChatRequest {
  message: string;
  conversation_id?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface AgentRequest {
  task: string;
  agent_type?: string;
  tools?: string[];
  max_iterations?: number;
}

// API Response Types
export interface ChatResponse {
  message: string;
  conversation_id: string;
  model_used: string;
  timestamp: string;
  metadata?: {
    temperature: number;
    memory_length: number;
    [key: string]: any;
  };
}

export interface AgentResponse {
  result: string;
  steps: AgentStep[];
  agent_type: string;
  timestamp: string;
  metadata?: {
    tools_used: string[];
    max_iterations: number;
    conversation_id: string;
    [key: string]: any;
  };
}

export interface AgentStep {
  step: number;
  action: string;
  input?: string;
  output?: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  ollama_status: string;
  uptime: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
  request_id?: string;
}

export interface ConversationHistory {
  conversation_id: string;
  messages: ChatMessage[];
  message_count: number;
  last_updated: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ModelInfo {
  name: string;
  type: string;
  status: string;
}

export interface ModelsResponse {
  current_model: string;
  ollama_base_url: string;
  models: ModelInfo[];
  timestamp: string;
}

export interface Tool {
  name: string;
  description: string;
  type: string;
}

export interface ToolsResponse {
  tools: Tool[];
  count: number;
  timestamp: string;
}

// Legacy API Types
export interface LegacyAskResponse {
  question: string;
  answer: string;
  conversation_id: string;
  timestamp: string;
} 