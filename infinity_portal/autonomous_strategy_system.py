from infinity_portal.data_collectors.social_media_collector import SocialMediaCollector
from infinity_portal.data_collectors.news_collector import NewsCollector
from infinity_portal.agents.edge_finder_agent import EdgeFinderAgent
from infinity_portal.agents.algorithm_generator import AlgorithmGeneratorAgent
from infinity_portal.agents.strategy_optimizer import StrategyOptimizerAgent
from infinity_portal.backtest.backtest_engine import BacktestEngine
from infinity_portal.dashboard_generator import TrustDashboard
from loguru import logger
import json
from datetime import datetime
from pathlib import Path

class AutonomousStrategySystem:
    """
    Complete autonomous trading strategy generation and optimization system
    
    Workflow:
    1. Collect social media + news data
    2. Find trading edges using AI
    3. Generate algorithm code
    4. Backtest 1Y and 5Y
    5. Compare with S&P500
    6. Optimize based on results
    7. Repeat until performance target met
    """
    
    def __init__(self, output_dir: str = "strategies"):
        self.social_collector = SocialMediaCollector()
        self.news_collector = NewsCollector()
        self.edge_finder = EdgeFinderAgent()
        self.algorithm_generator = AlgorithmGeneratorAgent()
        self.optimizer = StrategyOptimizerAgent()