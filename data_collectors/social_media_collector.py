import os
import tweepy
import requests
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger
from collections import Counter
import re

class SocialMediaCollector:
    """
    Collects and analyzes social media data for trading signals
    Focus: Twitter mentions, sentiment, volume trends
    """
    
    def __init__(self):
        # Twitter API v2 credentials
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        
        # StockTwits as alternative/supplement
        self.stocktwits_base = "https://api.stocktwits.com/api/2"
        
    def get_twitter_mentions(
        self, 
        ticker: str, 
        days_back: int = 7
    ) -> Dict:
        """
        Get Twitter mentions and sentiment for a stock ticker
        
        Returns:
            {
                'total_mentions': int,
                'sentiment_breakdown': dict,
                'volume_trend': list,
                'top_influencers': list,
                'viral_tweets': list
            }
        """
        try:
            # Search query
            query = f"${ticker} OR #{ticker} -is:retweet lang:en"
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            tweets = []
            
            # Use Twitter API v2 to search recent tweets
            response = self.client.search_recent_tweets(
                query=query,
                start_time=start_time,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'public_metrics']
            )
            
            if not response.data:
                logger.warning(f"No tweets found for {ticker}")
                return self._empty_response()
            
            # Process tweets
            tweets_data = []
            for tweet in response.data:
                tweets_data.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                })
            
            # Analyze
            total_mentions = len(tweets_data)
            
            # Simple sentiment analysis (would use LLM for better accuracy)
            sentiment_breakdown = self._analyze_sentiment_batch(tweets_data)
            
            # Volume trend (mentions per day)
            volume_trend = self._calculate_volume_trend(tweets_data, days_back)
            
            # Identify viral tweets (high engagement)
            viral_tweets = sorted(
                tweets_data, 
                key=lambda x: x['likes'] + x['retweets'], 
                reverse=True
            )[:5]
            
            return {
                'total_mentions': total_mentions,
                'sentiment_breakdown': sentiment_breakdown,
                'volume_trend': volume_trend,
                'viral_tweets': viral_tweets,
                'mention_velocity': total_mentions / days_back,  # Mentions per day
                'data_quality': 'high' if total_mentions > 50 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Twitter data: {e}")
            return self._empty_response()
    
    def get_stocktwits_sentiment(self, ticker: str) -> Dict:
        """
        Get sentiment from StockTwits (free API)
        """
        try:
            url = f"{self.stocktwits_base}/streams/symbol/{ticker}.json"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get('messages', [])
            
            bullish = sum(1 for m in messages if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bullish')
            bearish = sum(1 for m in messages if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bearish')
            total = len(messages)
            
            return {
                'bullish_percent': (bullish / total * 100) if total > 0 else 0,
                'bearish_percent': (bearish / total * 100) if total > 0 else 0,
                'neutral_percent': ((total - bullish - bearish) / total * 100) if total > 0 else 0,
                'total_messages': total,
                'sentiment_score': (bullish - bearish) / total if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"StockTwits error: {e}")
            return {}
    
    def _analyze_sentiment_batch(self, tweets: List[Dict]) -> Dict:
        """
        Analyze sentiment of tweet batch
        Uses keyword-based approach (can be enhanced with LLM)
        """
        positive_keywords = [
            'bull', 'bullish', 'moon', 'rocket', 'calls', 'long', 
            'buy', 'breakout', 'pump', 'ATH', 'green', 'profit'
        ]
        negative_keywords = [
            'bear', 'bearish', 'crash', 'dump', 'puts', 'short', 
            'sell', 'breakdown', 'red', 'loss', 'overvalued'
        ]
        
        bullish = 0
        bearish = 0
        neutral = 0
        
        for tweet in tweets:
            text = tweet['text'].lower()
            
            pos_count = sum(1 for word in positive_keywords if word in text)
            neg_count = sum(1 for word in negative_keywords if word in text)
            
            if pos_count > neg_count:
                bullish += 1
            elif neg_count > pos_count:
                bearish += 1
            else:
                neutral += 1
        
        total = len(tweets)
        
        return {
            'bullish_percent': (bullish / total * 100) if total > 0 else 0,
            'bearish_percent': (bearish / total * 100) if total > 0 else 0,
            'neutral_percent': (neutral / total * 100) if total > 0 else 0,
            'sentiment_score': (bullish - bearish) / total if total > 0 else 0
        }
    
    def _calculate_volume_trend(self, tweets: List[Dict], days: int) -> List[Dict]:
        """Calculate mentions per day trend"""
        daily_counts = {}
        
        for tweet in tweets:
            date = tweet['created_at'].date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        # Fill in missing days with 0
        start_date = datetime.utcnow().date() - timedelta(days=days)
        trend = []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            trend.append({
                'date': str(date),
                'mentions': daily_counts.get(date, 0)
            })
        
        return trend
    
    def _empty_response(self) -> Dict:
        """Return empty response structure"""
        return {
            'total_mentions': 0,
            'sentiment_breakdown': {
                'bullish_percent': 0,
                'bearish_percent': 0,
                'neutral_percent': 0,
                'sentiment_score': 0
            },
            'volume_trend': [],
            'viral_tweets': [],
            'mention_velocity': 0,
            'data_quality': 'none'
        }
    
    def calculate_social_score(self, ticker: str) -> Dict:
        """
        Calculate comprehensive social media score
        Combines Twitter and StockTwits data
        """
        twitter_data = self.get_twitter_mentions(ticker)
        stocktwits_data = self.get_stocktwits_sentiment(ticker)
        
        # Weighted average of sentiment
        twitter_sentiment = twitter_data['sentiment_breakdown']['sentiment_score']
        stocktwits_sentiment = stocktwits_data.get('sentiment_score', 0)
        
        # Weight by data volume
        twitter_weight = min(twitter_data['total_mentions'] / 100, 0.7)
        stocktwits_weight = 1 - twitter_weight
        
        combined_sentiment = (
            twitter_sentiment * twitter_weight + 
            stocktwits_sentiment * stocktwits_weight
        )
        
        # Calculate momentum (change in mentions over time)
        if len(twitter_data['volume_trend']) >= 7:
            recent_avg = sum(d['mentions'] for d in twitter_data['volume_trend'][-3:]) / 3
            older_avg = sum(d['mentions'] for d in twitter_data['volume_trend'][:3]) / 3
            momentum = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            momentum = 0
        
        return {
            'combined_sentiment': combined_sentiment,
            'mention_velocity': twitter_data['mention_velocity'],
            'momentum': momentum,
            'twitter_data': twitter_data,
            'stocktwits_data': stocktwits_data,
            'overall_score': (combined_sentiment + momentum) / 2,  # -1 to 1 scale
            'signal_strength': 'strong' if abs(combined_sentiment) > 0.5 else 'weak'
        }