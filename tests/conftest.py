import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_price_data():
    """Generate sample OHLCV data"""
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    
    data = pd.DataFrame({
        'Open': np.random.uniform(100, 200, len(dates)),
        'High': np.random.uniform(100, 200, len(dates)),
        'Low': np.random.uniform(100, 200, len(dates)),
        'Close': np.random.uniform(100, 200, len(dates)),
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    return data


@pytest.fixture
def sample_social_data():
    """Sample social media data"""
    return {
        'total_mentions': 150,
        'sentiment_breakdown': {
            'sentiment_score': 0.65,
            'bullish_percent': 70,
            'bearish_percent': 20,
            'neutral_percent': 10
        },
        'volume_trend': [
            {'date': '2024-01-01', 'mentions': 20},
            {'date': '2024-01-02', 'mentions': 25},
        ],
        'mention_velocity': 21.4,
        'data_quality': 'high'
    }


@pytest.fixture
def sample_news_data():
    """Sample news data"""
    return {
        'total_articles': 25,
        'sentiment_score': 0.55,
        'sentiment_trend': 'improving',
        'key_themes': ['earnings', 'product launch'],
        'articles': []
    }


@pytest.fixture
def sample_edge():
    """Sample trading edge"""
    return {
        'edge_id': 'test_edge_001',
        'edge_name': 'Sentiment Momentum',
        'edge_type': 'sentiment_momentum',
        'description': 'Test edge for unit testing',
        'entry_conditions': ['Sentiment > 0.6', 'Volume increasing'],
        'exit_conditions': ['Sentiment < 0.4', 'Price target hit'],
        'expected_sharpe': 1.8,
        'expected_win_rate': 0.62,
        'confidence': 0.75,
        'data_requirements': ['Twitter mentions', 'Price data'],
        'risk_factors': ['Low liquidity']
    }