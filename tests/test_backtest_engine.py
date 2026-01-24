import pytest
from infinity_portal.backtest.backtest_engine import BacktestEngine


def test_backtest_engine_initialization():
    """Test that backtest engine initializes correctly"""
    engine = BacktestEngine()
    assert engine.benchmark_ticker == 'SPY'


def test_fetch_historical_data():
    """Test data fetching"""
    engine = BacktestEngine()
    data = engine.fetch_historical_data('AAPL', years=1)
    
    assert data is not None
    assert len(data) > 0
    assert 'Close' in data.columns
