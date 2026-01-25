import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, TradeResponse, HistoricalAnalytics } from '@/types';
import { tradingApi } from '@/services/api';
import type { TradeStatus } from '@/types';
interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  apiKey: string | null;

  // Data
  trades: TradeResponse[];
  currentTrade: TradeResponse | null;
  analytics: HistoricalAnalytics | null;

  // UI State
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setApiKey: (key: string | null) => void;
  logout: () => void;

  // API Actions
  fetchProfile: () => Promise<void>;
  fetchTrades: (params?: {
    skip?: number;
    limit?: number;
    status?: TradeStatus | undefined;
  }) => Promise<void>;
  fetchTrade: (id: string) => Promise<void>;
  fetchAnalytics: (days?: number) => Promise<void>;
  createUser: (data: {
    username: string;
    email: string;
    fund_name: string;
    fund_description?: string;
  }) => Promise<User>;

  // Utilities
  clearError: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial State
      user: null,
      isAuthenticated: false,
      apiKey: null,
      trades: [],
      currentTrade: null,
      analytics: null,
      isLoading: false,
      error: null,

      // Basic Setters
      setUser: (user) =>
        set({ user, isAuthenticated: !!user }),

      setApiKey: (key) => {
        if (key) {
          localStorage.setItem('api_key', key);
        } else {
          localStorage.removeItem('api_key');
        }
        set({ apiKey: key, isAuthenticated: !!key });
      },

      logout: () => {
        localStorage.removeItem('api_key');
        set({
          user: null,
          apiKey: null,
          isAuthenticated: false,
          trades: [],
          currentTrade: null,
          analytics: null,
        });
      },

      // API Actions
      fetchProfile: async () => {
        set({ isLoading: true, error: null });
        try {
          const user = await tradingApi.getProfile();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Failed to fetch profile';
          set({ error: errorMsg, isLoading: false });
          throw err;
        }
      },

      fetchTrades: async (params) => {
        set({ isLoading: true, error: null });
        try {
          const trades = await tradingApi.getTrades(params);
          set({ trades, isLoading: false });
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Failed to fetch trades';
          set({ error: errorMsg, isLoading: false });
        }
      },

      fetchTrade: async (id) => {
        set({ isLoading: true, error: null });
        try {
          const trade = await tradingApi.getTrade(id);
          set({ currentTrade: trade, isLoading: false });
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Failed to fetch trade';
          set({ error: errorMsg, isLoading: false });
        }
      },

      fetchAnalytics: async (days = 30) => {
        set({ isLoading: true, error: null });
        try {
          const analytics = await tradingApi.getAnalytics(days);
          set({ analytics, isLoading: false });
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Failed to fetch analytics';
          set({ error: errorMsg, isLoading: false });
        }
      },

      createUser: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const user = await tradingApi.createUser(data);
          get().setApiKey(user.api_key);
          set({ user, isAuthenticated: true, isLoading: false });
          return user;
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Failed to create user';
          set({ error: errorMsg, isLoading: false });
          throw err;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'infinity-portal-storage',
      partialize: (state) => ({
        apiKey: state.apiKey,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
