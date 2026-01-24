# infinity_portal/divergence_detector.py (NEW FILE)

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger

class SentimentPriceDivergenceDetector:
    """
    Detects divergences between news sentiment and price movements
    """
    
    def __init__(self, finnhub_api_key: str = None):
        self.api_key = finnhub_api_key or os.getenv("FINNHUB_API_KEY")
        self.base_url = "https://finnhub.io/api/v1"
        
    def get_news_sentiment(
        self, 
        ticker: str, 
        days_back: int = 7
    ) -> Dict:
        """
        Fetch news sentiment from Finnhub
        
        Returns:
            {
                'sentiment_score': float (-1 to 1),
                'articles_count': int,
                'positive_count': int,
                'negative_count': int,
                'neutral_count': int
            }
        """
        try:
            # Finnhub company news endpoint
            url = f"{self.base_url}/company-news"
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'symbol': ticker,
                'from': from_date,
                'to': to_date,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            news_items = response.json()
            
            # Calculate aggregate sentiment
            total_sentiment = 0
            positive, negative, neutral = 0, 0, 0
            
            for article in news_items:
                sentiment = article.get('sentiment', 0)
                total_sentiment += sentiment
                
                if sentiment > 0.1:
                    positive += 1
                elif sentiment < -0.1:
                    negative += 1
                else:
                    neutral += 1
            
            avg_sentiment = total_sentiment / len(news_items) if news_items else 0
            
            return {
                'sentiment_score': avg_sentiment,
                'articles_count': len(news_items),
                'positive_count': positive,
                'negative_count': negative,
                'neutral_count': neutral,
                'raw_articles': news_items[:5]  # Store top 5 for context
            }
            
        except Exception as e:
            logger.error(f"Error fetching Finnhub sentiment: {e}")
            return {
                'sentiment_score': 0,
                'articles_count': 0,
                'error': str(e)
            }
    
    def get_price_movement(
        self, 
        ticker: str, 
        days_back: int = 7
    ) -> Dict:
        """
        Get price movement direction and magnitude
        Uses Finnhub quote endpoint
        """
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': ticker,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            quote = response.json()
            
            current_price = quote.get('c', 0)  # Current price
            change_percent = quote.get('dp', 0)  # Percent change
            
            return {
                'current_price': current_price,
                'change_percent': change_percent,
                'direction': 'up' if change_percent > 0 else 'down',
                'magnitude': abs(change_percent)
            }
            
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            return {
                'current_price': 0,
                'change_percent': 0,
                'error': str(e)
            }
    
    def detect_divergence(
        self, 
        ticker: str, 
        threshold: float = 0.3
    ) -> Dict:
        """
        Main divergence detection logic
        
        Args:
            ticker: Stock symbol
            threshold: Minimum divergence to flag (0-1 scale)
        
        Returns:
            {
                'has_divergence': bool,
                'divergence_type': str,
                'severity': str,
                'confidence': float,
                'explanation': str,
                'risk_code': str
            }
        """
        sentiment = self.get_news_sentiment(ticker)
        price = self.get_price_movement(ticker)
        
        sentiment_score = sentiment['sentiment_score']
        price_direction = 1 if price['direction'] == 'up' else -1
        price_magnitude = price['magnitude']
        
        # Calculate divergence
        # Positive sentiment should correlate with price up
        # Negative sentiment should correlate with price down
        expected_correlation = sentiment_score * price_direction
        
        # Divergence exists when:
        # - Sentiment is positive but price is down (bearish divergence)
        # - Sentiment is negative but price is up (bullish divergence)
        has_divergence = False
        divergence_type = None
        severity = "NONE"
        
        if sentiment_score > threshold and price_direction < 0:
            # Positive news but price falling
            has_divergence = True
            divergence_type = "BEARISH"
            severity = self._calculate_severity(
                abs(sentiment_score), 
                price_magnitude
            )
            explanation = (
                f"⚠️ BEARISH DIVERGENCE: News sentiment is positive "
                f"({sentiment_score:.2f}) but price is falling "
                f"({price['change_percent']:.2f}%). "
                f"This suggests market doesn't believe the good news, "
                f"or insiders may be selling."
            )
            risk_code = "FD02"
            
        elif sentiment_score < -threshold and price_direction > 0:
            # Negative news but price rising
            has_divergence = True
            divergence_type = "BULLISH"
            severity = self._calculate_severity(
                abs(sentiment_score), 
                price_magnitude
            )
            explanation = (
                f"🚀 BULLISH DIVERGENCE: News sentiment is negative "
                f"({sentiment_score:.2f}) but price is rising "
                f"({price['change_percent']:.2f}%). "
                f"This suggests institutional accumulation or "
                f"market pricing in better-than-expected outcomes."
            )
            risk_code = "FD02"
            
        else:
            explanation = (
                f"✓ No significant divergence detected. "
                f"Sentiment ({sentiment_score:.2f}) and price direction "
                f"({price['direction']}) are aligned."
            )
            risk_code = None
        
        # Confidence based on data quality
        confidence = self._calculate_confidence(sentiment, price)
        
        return {
            'has_divergence': has_divergence,
            'divergence_type': divergence_type,
            'severity': severity,
            'confidence': confidence,
            'explanation': explanation,
            'risk_code': risk_code,
            'sentiment_data': sentiment,
            'price_data': price,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_severity(
        self, 
        sentiment_magnitude: float, 
        price_magnitude: float
    ) -> str:
        """Calculate divergence severity"""
        combined_magnitude = sentiment_magnitude * price_magnitude
        
        if combined_magnitude > 5.0:
            return "HIGH"
        elif combined_magnitude > 2.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(
        self, 
        sentiment: Dict, 
        price: Dict
    ) -> float:
        """Calculate confidence in divergence detection"""
        confidence = 1.0
        
        # Reduce confidence if few articles
        if sentiment['articles_count'] < 5:
            confidence *= 0.7
        
        # Reduce confidence if price data has errors
        if 'error' in price:
            confidence *= 0.5
        
        # Reduce confidence if sentiment data has errors
        if 'error' in sentiment:
            confidence *= 0.5
        
        return round(confidence, 2)


# Example usage
if __name__ == "__main__":
    detector = SentimentPriceDivergenceDetector()
    result = detector.detect_divergence("NVDA")
    print(result)