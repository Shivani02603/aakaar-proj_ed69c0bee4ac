import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  status: string;
  storage_path: string;
}

export interface ChatSession {
  id: string;
  session_id: string;
  created_at: string;
  last_activity: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  query: string;
  answer: string;
  citations: Record<string, any>;
  created_at: string;
}

export const login = (data: LoginRequest) => api.post<LoginResponse>('/api/login', data);

export const register = (data: RegisterRequest) => api.post<UserResponse>('/api/register', data);

export const getMe = () => api.get<UserResponse>('/api/me');

export const listDocuments = () => api.get<Document[]>('/api/documents');

export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<Document>('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const deleteDocument = (documentId: string) => api.delete(`/api/documents/${documentId}`);

export const createChatSession = () => api.post<ChatSession>('/api/chat/session');

export const getChatHistory = (sessionId: string) =>
  api.get<ChatMessage[]>(`/api/chat/${sessionId}/history`);

export const ingestDocuments = (data: { document_ids: string[] }) =>
  api.post('/api/ai/ingest', data);

export const aiQuery = (data: { query: string; session_id: string }) =>
  api.post('/api/ai/query', data);

export const getPerformanceMetrics = () => api.get('/api/performance/metrics');

export const healthCheck = () => api.get('/api/reliability/health');

export const getScalabilityStats = () => api.get('/api/scalability/stats');

export const getSecurityStatus = () => api.get('/api/security/status');

export const getUsabilityFeedback = () => api.get('/api/usability/feedback');