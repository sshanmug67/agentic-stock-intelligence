import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface IntentRequest {
  intent_type: string;
  parameters: Record<string, any>;
  user_id?: string;
  priority?: number;
}

export interface IntentResponse {
  execution_id: string;
  intent_type: string;
  status: string;
  message: string;
}

export interface AgentExecution {
  agent_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  result?: Record<string, any>;
  error?: string;
}

export interface ExecutionRecord {
  execution_id: string;
  intent_type: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  parameters: Record<string, any>;
  retry_count: number;
  error_message?: string;
  agents: AgentExecution[];
  result?: Record<string, any>;
}

// API Methods
export const executeIntent = async (request: IntentRequest): Promise<IntentResponse> => {
  const response = await api.post('/intents/execute', request);
  return response.data;
};

export const getExecution = async (executionId: string): Promise<ExecutionRecord> => {
  const response = await api.get(`/executions/${executionId}`);
  return response.data;
};

export const listExecutions = async (limit: number = 50): Promise<ExecutionRecord[]> => {
  const response = await api.get('/executions', { params: { limit } });
  return response.data;
};

export const getIntentTypes = async () => {
  const response = await api.get('/intents/types');
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;