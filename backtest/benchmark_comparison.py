"""
Benchmark Comparison
Compare strategy performance against S&P500 and other benchmarks
"""

import pandas as pd
import numpy as np
from typing import Dict
import yfinance as yf
from loguru import logger


class BenchmarkComparison:
    """
    Compare strategy against market benchmarks
    """
    
    def __init__(self, benchmark_ticker: str = "SPY"):
        self.benchmark_ticker = benchmark_ticker
    
    def fetch_benchmark_data(
        self,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
    ) -> pd.Series:
        """
        Fetch benchmark returns
        """
        try:
            benchmark = yf.download(
                self.benchmark_ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            return benchmark['Close']
            
        except Exception as e:
            logger.error(f"Error fetching benchmark: {e}")
            return pd.Series()
    
    def calculate_alpha_beta(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict:
        """
        Calculate alpha and beta
        
        Returns:
            {
                'alpha': float (annualized excess return),
                'beta': float (sensitivity to market),
                'correlation': float
            }
        """
        # Align indices
        common_idx = strategy_returns.index.intersection(benchmark_returns.index)
        
        if len(common_idx) < 30:
            logger.warning("Insufficient overlapping data for alpha/beta calculation")
            return {'alpha': 0, 'beta': 1, 'correlation': 0}
        
        strategy_aligned = strategy_returns.loc[common_idx]
        benchmark_aligned = benchmark_returns.loc[common_idx]
        
        # Calculate beta (covariance / variance)
        covariance = np.cov(strategy_aligned, benchmark_aligned)[0][1]
        benchmark_variance = np.var(benchmark_aligned)
        
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
        
        # Calculate alpha (excess return)
        strategy_return = (1 + strategy_aligned.mean()) ** 252 - 1
        benchmark_return = (1 + benchmark_aligned.mean()) ** 252 - 1
        
        alpha = strategy_return - (beta * benchmark_return)
        
        # Correlation
        correlation = np.corrcoef(strategy_aligned, benchmark_aligned)[0][1]
        
        return {
            'alpha': alpha * 100,  # Convert to percentage
            'beta': beta,
            'correlation': correlation
        }
    
    def compare(
        self,
        strategy_equity: pd.Series,
        benchmark_equity: pd.Series
    ) -> Dict:
        """
        Complete comparison
        
        Returns:
            Comprehensive comparison metrics
        """
        strategy_returns = strategy_equity.pct_change().dropna()
        benchmark_returns = benchmark_equity.pct_change().dropna()
        
        alpha_beta = self.calculate_alpha_beta(strategy_returns, benchmark_returns)
        
        # Total returns
        strategy_total_return = ((strategy_equity.iloc[-1] / strategy_equity.iloc[0]) - 1) * 100
        benchmark_total_return = ((benchmark_equity.iloc[-1] / benchmark_equity.iloc[0]) - 1) * 100
        
        return {
            'strategy_return': strategy_total_return,
            'benchmark_return': benchmark_total_return,
            'outperformance': strategy_total_return - benchmark_total_return,
            'alpha': alpha_beta['alpha'],
            'beta': alpha_beta['beta'],
            'correlation': alpha_beta['correlation'],
            'beats_benchmark': strategy_total_return > benchmark_total_return
        }