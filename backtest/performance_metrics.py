
import pandas as pd
import numpy as np
from typing import Dict


class PerformanceMetrics:
    """
    Calculate comprehensive trading performance metrics
    """
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate annualized Sharpe ratio
        
        Args:
            returns: Daily returns series
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Sharpe ratio
        """
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sortino ratio (uses downside deviation)
        """
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
        return sortino
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown percentage
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        return abs(drawdown.min()) * 100
    
    @staticmethod
    def calculate_calmar_ratio(
        returns: pd.Series,
        max_drawdown: float
    ) -> float:
        """
        Calculate Calmar ratio (return / max drawdown)
        """
        if max_drawdown == 0:
            return 0.0
        
        annual_return = (1 + returns.mean()) ** 252 - 1
        return annual_return / (max_drawdown / 100)
    
    @staticmethod
    def calculate_win_rate(trades: pd.DataFrame) -> float:
        """
        Calculate percentage of winning trades
        
        Args:
            trades: DataFrame with 'pnl' column
        
        Returns:
            Win rate as percentage
        """
        if len(trades) == 0:
            return 0.0
        
        winning_trades = len(trades[trades['pnl'] > 0])
        return (winning_trades / len(trades)) * 100
    
    @staticmethod
    def calculate_profit_factor(trades: pd.DataFrame) -> float:
        """
        Calculate profit factor (gross profits / gross losses)
        """
        if len(trades) == 0:
            return 0.0
        
        gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def calculate_all_metrics(
        returns: pd.Series,
        equity_curve: pd.Series,
        trades: pd.DataFrame
    ) -> Dict:
        """
        Calculate all performance metrics at once
        
        Returns:
            Dictionary with all metrics
        """
        max_dd = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        return {
            'sharpe_ratio': PerformanceMetrics.calculate_sharpe_ratio(returns),
            'sortino_ratio': PerformanceMetrics.calculate_sortino_ratio(returns),
            'max_drawdown': max_dd,
            'calmar_ratio': PerformanceMetrics.calculate_calmar_ratio(returns, max_dd),
            'win_rate': PerformanceMetrics.calculate_win_rate(trades),
            'profit_factor': PerformanceMetrics.calculate_profit_factor(trades),
            'total_return': ((equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1) * 100,
            'annual_return': ((1 + returns.mean()) ** 252 - 1) * 100,
            'annual_volatility': returns.std() * np.sqrt(252) * 100
        }