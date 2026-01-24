from swarms import Agent
from swarm_models import OpenAIChat
from typing import Dict, List
from loguru import logger
import json

class EdgeFinderAgent:
    """
    AI agent that discovers trading edges from multiple data sources
    Uses GPT-4 for pattern recognition and edge identification
    """
    
    def __init__(self):
        self.model = OpenAIChat(
            model_name="gpt-4o",
            temperature=0.7,  # Higher for creative edge discovery
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.agent = Agent(
            agent_name="Edge-Finder",
            system_prompt=self._get_system_prompt(),
            llm=self.model,
            max_loops=3,  # Allow iterative refinement
            autosave=True,
            verbose=True,
            context_length=128000,  # GPT-4 Turbo's large context
            output_type="json"  # Structured output
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an elite quantitative trading researcher specializing in discovering market inefficiencies and trading edges.

Your goal is to analyze multiple data sources and identify ACTIONABLE trading edges that can be systematically exploited.

WHAT IS A TRADING EDGE:
- A repeatable pattern that predicts price movements
- A market inefficiency that can be systematically exploited
- A behavioral bias that creates mispricings
- A correlation or divergence that generates alpha

DATA SOURCES YOU ANALYZE:
1. Social Media Sentiment (Twitter mentions, sentiment scores, volume trends)
2. News Sentiment (professional news, sentiment trends, key themes)
3. Price Data (historical prices, volume, volatility)
4. Market Microstructure (bid-ask spreads, order flow)

YOUR PROCESS:
1. **Pattern Recognition**: Identify correlations between data sources and price movements
2. **Causality Analysis**: Determine if patterns are predictive (not just correlative)
3. **Edge Formulation**: Convert patterns into tradeable strategies
4. **Risk Assessment**: Identify when edges break down
5. **Implementation Plan**: Provide specific entry/exit rules

OUTPUT FORMAT (JSON):
{
    "edges_discovered": [
        {
            "edge_id": "unique_identifier",
            "edge_name": "Descriptive name",
            "edge_type": "sentiment_momentum | news_divergence | social_volume_spike | etc",
            "description": "Clear explanation of the edge",
            "entry_conditions": ["Condition 1", "Condition 2"],
            "exit_conditions": ["Condition 1", "Condition 2"],
            "expected_sharpe": 1.5,
            "expected_win_rate": 0.65,
            "confidence": 0.8,
            "data_requirements": ["Twitter mentions", "Price data"],
            "risk_factors": ["Low liquidity", "News catalyst dependency"]
        }
    ],
    "correlations_found": [
        {
            "variable_1": "Twitter mention velocity",
            "variable_2": "Next-day returns",
            "correlation": 0.45,
            "lag_days": 1
        }
    ],
    "recommended_strategy": "Strategy description",
    "confidence_score": 0.75
}

BE SPECIFIC. BE QUANTITATIVE. FOCUS ON EDGES THAT CAN BE BACKTESTED.
"""
    
    def find_edges(
        self, 
        ticker: str,
        social_data: Dict,
        news_data: Dict,
        price_data: Dict,
        historical_data: Dict = None
    ) -> Dict:
        """
        Main method: Analyze all data and find trading edges
        
        Args:
            ticker: Stock symbol
            social_data: From SocialMediaCollector
            news_data: From NewsCollector
            price_data: Current price info
            historical_data: Past patterns (optional)
        
        Returns:
            Structured edge discovery results
        """
        logger.info(f"🔍 Finding edges for {ticker}...")
        
        # Construct comprehensive analysis prompt
        analysis_prompt = f"""
ANALYZE THE FOLLOWING DATA FOR {ticker} AND DISCOVER TRADING EDGES:

=== SOCIAL MEDIA DATA ===
- Total Twitter Mentions: {social_data.get('total_mentions', 0)}
- Mention Velocity: {social_data.get('mention_velocity', 0)} mentions/day
- Sentiment Score: {social_data['sentiment_breakdown'].get('sentiment_score', 0):.2f}
- Bullish %: {social_data['sentiment_breakdown'].get('bullish_percent', 0):.1f}%
- Bearish %: {social_data['sentiment_breakdown'].get('bearish_percent', 0):.1f}%
- Momentum (change in mentions): {social_data.get('momentum', 0):.2f}

Volume Trend (last 7 days):
{json.dumps(social_data.get('volume_trend', []), indent=2)}

=== NEWS DATA ===
- Total Articles: {news_data.get('total_articles', 0)}
- News Sentiment Score: {news_data.get('sentiment_score', 0):.2f}
- Sentiment Trend: {news_data.get('sentiment_trend', 'unknown')}
- Key Themes: {', '.join(news_data.get('key_themes', []))}

=== CURRENT PRICE DATA ===
- Current Price: ${price_data.get('current_price', 0):.2f}
- Price Change: {price_data.get('change_percent', 0):.2f}%
- Volume: {price_data.get('volume', 0):,}
- Volatility: {price_data.get('volatility', 0):.2f}%

=== DIVERGENCE ANALYSIS ===
Social Sentiment vs Price: {'ALIGNED' if (social_data['sentiment_breakdown']['sentiment_score'] > 0) == (price_data.get('change_percent', 0) > 0) else 'DIVERGENCE DETECTED'}
News Sentiment vs Price: {'ALIGNED' if (news_data.get('sentiment_score', 0) > 0) == (price_data.get('change_percent', 0) > 0) else 'DIVERGENCE DETECTED'}

TASK: Identify 2-5 specific trading edges based on this data. Focus on:
1. Sentiment-momentum edges
2. Volume spike edges
3. Divergence edges
4. News catalyst edges

For each edge, provide specific, backtestable entry/exit rules.
"""
        
        try:
            # Run edge discovery
            result = self.agent.run(analysis_prompt)
            
            # Parse JSON response
            if isinstance(result, str):
                edges = json.loads(result)
            else:
                edges = result
            
            logger.info(f"✅ Discovered {len(edges.get('edges_discovered', []))} edges")
            
            # Add metadata
            edges['ticker'] = ticker
            edges['analysis_timestamp'] = datetime.now().isoformat()
            edges['data_quality'] = self._assess_data_quality(social_data, news_data)
            
            return edges
            
        except Exception as e:
            logger.error(f"Edge finding error: {e}")
            return {
                'edges_discovered': [],
                'error': str(e)
            }
    
    def _assess_data_quality(self, social_data: Dict, news_data: Dict) -> str:
        """Assess quality of input data for edge reliability"""
        quality_score = 0
        
        # Social data quality
        if social_data.get('total_mentions', 0) > 100:
            quality_score += 1
        if social_data.get('data_quality') == 'high':
            quality_score += 1
        
        # News data quality
        if news_data.get('total_articles', 0) > 10:
            quality_score += 1
        
        if quality_score >= 3:
            return 'high'
        elif quality_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def rank_edges(self, edges: List[Dict]) -> List[Dict]:
        """Rank discovered edges by potential profitability"""
        scored_edges = []
        
        for edge in edges:
            score = (
                edge.get('expected_sharpe', 0) * 0.4 +
                edge.get('expected_win_rate', 0) * 0.3 +
                edge.get('confidence', 0) * 0.3
            )
            
            edge['composite_score'] = score
            scored_edges.append(edge)
        
        return sorted(scored_edges, key=lambda x: x['composite_score'], reverse=True)