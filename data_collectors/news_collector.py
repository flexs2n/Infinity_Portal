# infinity_portal/data_collectors/news_collector.py (NEW FILE)

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger

class NewsCollector:
    """
    Enhanced news collection with multiple sources and sentiment analysis
    """
    
    def __init__(self):
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
    
    def get_comprehensive_news(
        self, 
        ticker: str, 
        days_back: int = 7
    ) -> Dict:
        """
        Aggregate news from multiple sources
        
        Returns:
            {
                'total_articles': int,
                'sentiment_score': float,
                'sentiment_trend': str,
                'key_themes': list,
                'sources': dict
            }
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        all_articles = []
        
        # Finnhub news
        finnhub_news = self._get_finnhub_news(ticker, from_date, to_date)
        all_articles.extend(finnhub_news)
        
        # NewsAPI
        newsapi_news = self._get_newsapi_news(ticker, from_date, to_date)
        all_articles.extend(newsapi_news)
        
        # AlphaVantage
        av_news = self._get_alphavantage_news(ticker)
        all_articles.extend(av_news)
        
        # Analyze aggregated news
        analysis = self._analyze_news_sentiment(all_articles)
        
        return {
            'total_articles': len(all_articles),
            'sentiment_score': analysis['sentiment_score'],
            'sentiment_trend': analysis['trend'],
            'key_themes': analysis['themes'],
            'articles': all_articles[:20],  # Top 20 most recent
            'sources': {
                'finnhub': len(finnhub_news),
                'newsapi': len(newsapi_news),
                'alphavantage': len(av_news)
            }
        }
    
    def _get_finnhub_news(self, ticker: str, from_date: str, to_date: str) -> List[Dict]:
        """Get news from Finnhub"""
        try:
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': ticker,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            articles = response.json()
            
            return [{
                'source': 'finnhub',
                'headline': a.get('headline', ''),
                'summary': a.get('summary', ''),
                'url': a.get('url', ''),
                'datetime': a.get('datetime', 0),
                'sentiment': a.get('sentiment', 0)
            } for a in articles]
            
        except Exception as e:
            logger.error(f"Finnhub news error: {e}")
            return []
    
    def _get_newsapi_news(self, ticker: str, from_date: str, to_date: str) -> List[Dict]:
        """Get news from NewsAPI"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': ticker,
                'from': from_date,
                'to': to_date,
                'apiKey': self.newsapi_key,
                'language': 'en',
                'sortBy': 'relevancy'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            return [{
                'source': 'newsapi',
                'headline': a.get('title', ''),
                'summary': a.get('description', ''),
                'url': a.get('url', ''),
                'datetime': int(datetime.fromisoformat(
                    a.get('publishedAt', '').replace('Z', '+00:00')
                ).timestamp()) if a.get('publishedAt') else 0,
                'sentiment': 0  # Will be calculated
            } for a in articles]
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    def _get_alphavantage_news(self, ticker: str) -> List[Dict]:
        """Get news from Alpha Vantage"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': self.alphavantage_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            feed = data.get('feed', [])
            
            return [{
                'source': 'alphavantage',
                'headline': a.get('title', ''),
                'summary': a.get('summary', ''),
                'url': a.get('url', ''),
                'datetime': int(datetime.fromisoformat(
                    a.get('time_published', '')[:8] + 'T' + 
                    a.get('time_published', '')[9:]
                ).timestamp()) if a.get('time_published') else 0,
                'sentiment': float(a.get('overall_sentiment_score', 0))
            } for a in feed]
            
        except Exception as e:
            logger.error(f"AlphaVantage news error: {e}")
            return []
    
    def _analyze_news_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze aggregated news sentiment"""
        if not articles:
            return {
                'sentiment_score': 0,
                'trend': 'neutral',
                'themes': []
            }
        
        # Calculate average sentiment
        sentiments = [a['sentiment'] for a in articles if a.get('sentiment')]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Determine trend (compare recent vs older articles)
        sorted_articles = sorted(articles, key=lambda x: x['datetime'], reverse=True)
        mid_point = len(sorted_articles) // 2
        
        recent_sentiment = sum(
            a['sentiment'] for a in sorted_articles[:mid_point] if a.get('sentiment')
        ) / mid_point if mid_point > 0 else 0
        
        older_sentiment = sum(
            a['sentiment'] for a in sorted_articles[mid_point:] if a.get('sentiment')
        ) / (len(sorted_articles) - mid_point) if len(sorted_articles) > mid_point else 0
        
        if recent_sentiment > older_sentiment + 0.1:
            trend = 'improving'
        elif recent_sentiment < older_sentiment - 0.1:
            trend = 'deteriorating'
        else:
            trend = 'stable'
        
        # Extract key themes (simple keyword extraction)
        all_text = ' '.join([a['headline'] + ' ' + a['summary'] for a in articles])
        # This would be enhanced with LLM for better theme extraction
        themes = self._extract_themes(all_text)
        
        return {
            'sentiment_score': avg_sentiment,
            'trend': trend,
            'themes': themes
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes from text (simplified)"""
        # In production, use LLM or NLP library
        keywords = [
            'earnings', 'revenue', 'acquisition', 'merger', 
            'lawsuit', 'FDA', 'regulation', 'partnership',
            'product', 'launch', 'CEO', 'growth', 'decline'
        ]
        
        text_lower = text.lower()
        found_themes = [kw for kw in keywords if kw in text_lower]
        
        return found_themes[:5]  # Top 5 themes