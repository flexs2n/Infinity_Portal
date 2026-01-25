export type TradeStatus =
  | 'pending'
  | 'executing'
  | 'completed'
  | 'failed';

export interface UserCreate {
  username: string;
  email: string;
  fund_name: string;
  fund_description?: string;
}

export interface UserUpdate {
  fund_name?: string;
  fund_description?: string;
  email?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  fund_name: string;
  fund_description?: string;
  api_key: string;
  created_at: string;
  last_login?: string;
  is_active: boolean;
}

export interface TradingTask {
  stocks: string[];
  task: string;
  allocation: number;
  strategy_type?: string;
  risk_level?: number;
}

export interface PerformanceMetrics {
  return_percentage: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
}

export interface TradeResult {
  trading_thesis?: string;
  quantitative_analysis?: string;
  sentiment_analysis?: string;
  risk_assessment?: string;
  execution_order?: string;
  final_decision?: string;
  confidence_score?: number;
  recommended_action?: 'BUY' | 'SELL' | 'HOLD';
  entry_price?: number;
  stop_loss?: number;
  take_profit?: number;
  position_size?: number;
  [key: string]: unknown;
}

export interface TradeResponse {
  id: string;
  user_id: string;
  task: TradingTask;
  status: TradeStatus;
  created_at: string;
  executed_at?: string;
  result?: TradeResult;
  performance_metrics?: PerformanceMetrics;
}

export interface HistoricalAnalytics {
  total_trades: number;
  success_rate: number;
  average_return: number;
  total_allocation: number;
  risk_adjusted_return: number;
  top_performing_stocks: [string, number][];
}

export interface TradesListParams {
  skip?: number;
  limit?: number;
  status?: TradeStatus;
}
