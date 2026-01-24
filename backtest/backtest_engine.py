import vectorbt as vbt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
from loguru import logger
import yfinance as yf

class BacktestEngine:
    """
    Professional backtesting engine using vectorbt
    Supports 1-year and 5-year backtests with S&P500 comparison
    """
    
    def __init__(self):
        self.vbt = vbt
        self.benchmark_ticker = 'SPY'  # S&P500 ETF
    
    def fetch_historical_data(
        self,
        ticker: str,
        years: int = 5
    ) -> pd.DataFrame:
        """
        Fetch historical price data
        
        Args:
            ticker: Stock symbol
            years: Number of years of history
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            logger.info(f"📥 Fetching {years}Y data for {ticker}...")
            
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if data.empty:
                logger.error(f"No data retrieved for {ticker}")
                return None
            
            logger.info(f"✅ Retrieved {len(data)} days of data")
            return data
            
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return None
    
    def fetch_social_historical_data(
        self,
        ticker: str,
        years: int = 5
    ) -> pd.DataFrame:
        """
        Fetch historical social media data
        NOTE: Historical Twitter data requires premium API access
        This is a placeholder for demonstration
        """
        # In production, you'd use:
        # - Twitter Academic API
        # - Purchased historical sentiment datasets
        # - Alternative data providers (Quiver Quantitative, etc.)
        
        logger.warning("Historical social data requires premium APIs")
        
        # Generate synthetic social data for demonstration
        price_data = self.fetch_historical_data(ticker, years)
        if price_data is None:
            return None
        
        # Simulate social sentiment (correlated with returns + noise)
        returns = price_data['Close'].pct_change()
        
        social_data = pd.DataFrame(index=price_data.index)
        social_data['sentiment'] = (
            returns.rolling(5).mean() + 
            np.random.normal(0, 0.1, len(price_data))
        )
        social_data['mentions'] = np.abs(
            np.random.normal(100, 50, len(price_data))
        )
        
        return social_data
    
    def run_backtest(
        self,
        algorithm_code: str,
        ticker: str,
        years: int = 5,
        initial_capital: float = 100000
    ) -> Dict:
        """
        Run backtest of algorithm
        
        Args:
            algorithm_code: Python code of strategy
            ticker: Stock to trade
            years: Backtest period
            initial_capital: Starting capital
        
        Returns:
            Comprehensive backtest results
        """
        try:
            logger.info(f"🧪 Running {years}Y backtest for {ticker}...")
            
            # Fetch data
            price_data = self.fetch_historical_data(ticker, years)
            social_data = self.fetch_social_historical_data(ticker, years)
            
            if price_data is None:
                return {'error': 'Data fetch failed'}
            
            # Execute algorithm code to get strategy class
            exec_globals = {
                'vbt': vbt,
                'pd': pd,
                'np': np
            }
            exec(algorithm_code, exec_globals)
            
            # Find strategy class (assumes class name ends with 'Strategy')
            strategy_class = None
            for name, obj in exec_globals.items():
                if isinstance(obj, type) and name.endswith('Strategy'):
                    strategy_class = obj
                    break
            
            if not strategy_class:
                return {'error': 'No strategy class found in code'}
            
            # Initialize strategy
            strategy = strategy_class(params={})
            
            # Generate signals
            entries, exits = strategy.generate_signals(
                price_data=price_data,
                social_data=social_data,
                news_data=pd.DataFrame()  # Placeholder
            )
            
            # Run vectorbt portfolio simulation
            portfolio = vbt.Portfolio.from_signals(
                close=price_data['Close'],
                entries=entries,
                exits=exits,
                init_cash=initial_capital,
                fees=0.001,  # 0.1% trading fees
                slippage=0.0005,  # 0.05% slippage
                freq='1D'
            )
            
            # Calculate metrics
            results = self._calculate_metrics(portfolio, price_data, ticker)
            
            # Compare with S&P500
            benchmark_comparison = self._compare_with_benchmark(
                portfolio, 
                ticker,
                years
            )
            
            results['benchmark_comparison'] = benchmark_comparison
            results['backtest_period'] = f"{years} years"
            results['ticker'] = ticker
            
            logger.info(f"✅ Backtest complete!")
            logger.info(f"   Total Return: {results['total_return']:.2f}%")
            logger.info(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            logger.info(f"   Max Drawdown: {results['max_drawdown']:.2f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _calculate_metrics(
        self,
        portfolio: vbt.Portfolio,
        price_data: pd.DataFrame,
        ticker: str
    ) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        # Basic metrics
        total_return = portfolio.total_return() * 100
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown() * 100
        win_rate = portfolio.win_rate() * 100
        
        # Advanced metrics
        sortino_ratio = portfolio.sortino_ratio()
        calmar_ratio = portfolio.calmar_ratio()
        
        # Trade statistics
        total_trades = portfolio.trades.count()
        avg_trade_duration = portfolio.trades.duration.mean()
        
        # Return statistics
        returns = portfolio.returns()
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'avg_trade_duration_days': avg_trade_duration.days if hasattr(avg_trade_duration, 'days') else 0,
            'best_month': monthly_returns.max() * 100,
            'worst_month': monthly_returns.min() * 100,
            'positive_months': (monthly_returns > 0).sum(),
            'negative_months': (monthly_returns < 0).sum(),
            'final_portfolio_value': portfolio.final_value(),
            'total_fees_paid': portfolio.total_fees()
        }
    
    def _compare_with_benchmark(
        self,
        portfolio: vbt.Portfolio,
        ticker: str,
        years: int
    ) -> Dict:
        """Compare strategy performance with S&P500"""
        try:
            # Fetch S&P500 data
            spy_data = self.fetch_historical_data(self.benchmark_ticker, years)
            
            if spy_data is None:
                return {'error': 'Benchmark data unavailable'}
            
            # Buy and hold S&P500
            spy_returns = (spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[0] - 1) * 100
            
            # Strategy returns
            strategy_returns = portfolio.total_return() * 100
            
            # Alpha calculation (excess return)
            alpha = strategy_returns - spy_returns
            
            # Beta calculation (volatility relative to market)
            portfolio_returns = portfolio.returns()
            spy_daily_returns = spy_data['Close'].pct_change().dropna()
            
            # Align indices
            common_idx = portfolio_returns.index.intersection(spy_daily_returns.index)
            portfolio_returns_aligned = portfolio_returns.loc[common_idx]
            spy_returns_aligned = spy_daily_returns.loc[common_idx]
            
            # Calculate beta
            covariance = np.cov(portfolio_returns_aligned, spy_returns_aligned)[0][1]
            market_variance = np.var(spy_returns_aligned)
            beta = covariance / market_variance if market_variance != 0 else 1.0
            
            return {
                'sp500_return': spy_returns,
                'strategy_return': strategy_returns,
                'alpha': alpha,
                'beta': beta,
                'outperformance': alpha > 0,
                'relative_sharpe': portfolio.sharpe_ratio() / vbt.Portfolio.from_holding(spy_data['Close']).sharpe_ratio() if vbt.Portfolio.from_holding(spy_data['Close']).sharpe_ratio() != 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Benchmark comparison error: {e}")
            return {'error': str(e)}
    
    def run_multiple_backtests(
        self,
        algorithm_code: str,
        ticker: str,
        periods: List[int] = [1, 5]
    ) -> Dict:
        """
        Run backtests for multiple time periods
        
        Args:
            algorithm_code: Strategy code
            ticker: Stock symbol
            periods: List of years to backtest (e.g., [1, 5])
        
        Returns:
            Results for each period
        """
        results = {}
        
        for years in periods:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running {years}-year backtest...")
            logger.info(f"{'='*60}\n")
            
            result = self.run_backtest(
                algorithm_code=algorithm_code,
                ticker=ticker,
                years=years
            )
            
            results[f'{years}Y'] = result
        
        # Compare consistency across periods
        results['consistency_analysis'] = self._analyze_consistency(results)
        
        return results
    
    def _analyze_consistency(self, results: Dict) -> Dict:
        """Analyze consistency of strategy across different time periods"""
        sharpe_ratios = []
        returns = []
        
        for period, data in results.items():
            if period != 'consistency_analysis' and 'error' not in data:
                sharpe_ratios.append(data['sharpe_ratio'])
                returns.append(data['total_return'])
        
        if not sharpe_ratios:
            return {}
        
        return {
            'sharpe_consistency': np.std(sharpe_ratios),  # Lower is better
            'return_consistency': np.std(returns),
            'avg_sharpe': np.mean(sharpe_ratios),
            'avg_return': np.mean(returns),
            'is_consistent': np.std(sharpe_ratios) < 0.5  # Arbitrary threshold
        }