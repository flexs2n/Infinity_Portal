import axios, { AxiosError } from 'axios';
import type {
  User,
  UserCreate,
  UserUpdate,
  TradingTask,
  TradeResponse,
  HistoricalAnalytics,
  TradesListParams,
} from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Key interceptor
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Error handler interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('api_key');
      window.location.href = '/onboarding';
    }
    return Promise.reject(error);
  }
);

export const tradingApi = {
  // Users
  createUser: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  updateProfile: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    return response.data;
  },

  // Trades
  createTrade: async (data: TradingTask): Promise<TradeResponse> => {
    const response = await apiClient.post<TradeResponse>('/trades', data);
    return response.data;
  },

  getTrades: async (
    params?: TradesListParams
  ): Promise<TradeResponse[]> => {
    const response = await apiClient.get<TradeResponse[]>('/trades', {
      params,
    });
    return response.data;
  },

  getTrade: async (id: string): Promise<TradeResponse> => {
    const response = await apiClient.get<TradeResponse>(`/trades/${id}`);
    return response.data;
  },

  deleteTrade: async (id: string): Promise<void> => {
    await apiClient.delete(`/trades/${id}`);
  },

  // Analytics
  getAnalytics: async (days: number = 30): Promise<HistoricalAnalytics> => {
    const response = await apiClient.get<HistoricalAnalytics>(
      `/analytics/history?days=${days}`
    );
    return response.data;
  },
};

export default apiClient;
