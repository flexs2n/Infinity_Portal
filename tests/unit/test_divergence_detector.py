"""
Unit Tests for Divergence Detector
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infinity_portal.divergence_detector import SentimentPriceDivergenceDetector


class TestDivergenceDetector:
    """Test suite for SentimentPriceDivergenceDetector"""
    
    def test_initialization(self):
        """Test detector initializes correctly"""
        detector = SentimentPriceDivergenceDetector()
        assert detector.base_url == "https://finnhub.io/api/v1"
    
    @patch('infinity_portal.divergence_detector.requests.get')
    def test_detect_bullish_divergence(self, mock_get):
        """Test bullish divergence detection"""
        # Mock API responses
        mock_sentiment = Mock()
        mock_sentiment.status_code = 200
        mock_sentiment.json.return_value = [
            {'sentiment': -0.6, 'headline': 'Bad news'}
        ]
        
        mock_price = Mock()
        mock_price.status_code = 200
        mock_price.json.return_value = {
            'c': 500,
            'dp': 5.0  # 5% price increase
        }
        
        mock_get.side_effect = [mock_sentiment, mock_price]
        
        detector = SentimentPriceDivergenceDetector(finnhub_api_key="test_key")
        result = detector.detect_divergence("TEST", threshold=0.3)
        
        assert result['has_divergence'] == True
        assert result['divergence_type'] == 'BULLISH'
    
    @patch('infinity_portal.divergence_detector.requests.get')
    def test_no_divergence(self, mock_get):
        """Test when no divergence exists"""
        mock_sentiment = Mock()
        mock_sentiment.status_code = 200
        mock_sentiment.json.return_value = [
            {'sentiment': 0.5, 'headline': 'Good news'}
        ]
        
        mock_price = Mock()
        mock_price.status_code = 200
        mock_price.json.return_value = {
            'c': 500,
            'dp': 3.0  # Positive price, positive sentiment = aligned
        }
        
        mock_get.side_effect = [mock_sentiment, mock_price]
        
        detector = SentimentPriceDivergenceDetector(finnhub_api_key="test_key")
        result = detector.detect_divergence("TEST")
        
        assert result['has_divergence'] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])