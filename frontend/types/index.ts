export * from './api';

// Import specific types for proper referencing
import type { AgentRequest, AgentResponse } from './api';

// UI State Types
export interface AppState {
  isLoading: boolean;
  error: string | null;
  currentConversation: string | null;
  conversations: Record<string, ConversationState>;
  settings: AppSettings;
}

export interface ConversationState {
  id: string;
  messages: UIMessage[];
  isLoading: boolean;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface UIMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  isLoading?: boolean;
  error?: string;
  metadata?: Record<string, any>;
}

export interface AppSettings {
  apiUrl: string;
  defaultModel: string;
  temperature: number;
  maxTokens: number;
  theme: 'light' | 'dark' | 'system';
  autoScroll: boolean;
  showTimestamps: boolean;
  enableSound: boolean;
}

// Component Props Types
export interface ChatInputProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export interface MessageProps {
  message: UIMessage;
  showTimestamp?: boolean;
  onRegenerate?: () => void;
  onCopy?: () => void;
}

export interface ConversationListProps {
  conversations: ConversationState[];
  currentConversationId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onNew: () => void;
}

export interface SettingsProps {
  settings: AppSettings;
  onUpdate: (settings: Partial<AppSettings>) => void;
  onReset: () => void;
}

// Hook Types
export interface UseApiResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UseChatResult {
  messages: UIMessage[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  clearConversation: () => void;
}

export interface UseAgentResult {
  runAgent: (task: string, options?: Partial<AgentRequest>) => Promise<AgentResponse>;
  isLoading: boolean;
  error: string | null;
  lastResult: AgentResponse | null;
}

// Utility Types
export type ApiStatus = 'online' | 'offline' | 'error' | 'unknown';

export interface NotificationOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
}

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  description: string;
  action: () => void;
}

// Form Types
export interface ChatFormData {
  message: string;
  temperature: number;
  maxTokens: number;
  model: string;
}

export interface AgentFormData {
  task: string;
  agentType: string;
  tools: string[];
  maxIterations: number;
}

// Error Types
export class ApiError extends Error {
  status: number;
  code?: string;
  
  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export class NetworkError extends Error {
  status: number = 0;
  
  constructor(message: string = 'Network error occurred') {
    super(message);
    this.name = 'NetworkError';
    this.status = 0;
  }
}

// Re-export from api.ts for convenience
export type {
  ChatRequest,
  ChatResponse,
  AgentRequest,
  AgentResponse,
  HealthResponse,
  ErrorResponse,
  ConversationHistory,
  ChatMessage,
  ModelsResponse,
  ToolsResponse
} from './api'; 