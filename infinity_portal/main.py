"""
AutoHedge Main Module
Core trading system with multi-agent architecture and enhanced features

This module provides the main AutoHedge class that coordinates:
- Trading Director (strategy generation)
- Quantitative Analyst (technical analysis)
- Risk Manager (position sizing & risk assessment)
- Execution Agent (trade order generation)
- Sentiment Analysis (market sentiment from news/social media)
- Divergence Detection (sentiment-price misalignment)
- Exchange Monitoring (multi-source price validation)
- Interactive Trader Interface (human-in-the-loop decision making)

Author: The Swarm Corporation
Version: 2.0.0
"""

import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from loguru import logger
from pydantic import BaseModel, Field
from swarms import Agent, Conversation

# Lazy import to avoid initialization at module load time
TickrAgent = None

# Import new components
try:
    from autohedge.divergence_detector import SentimentPriceDivergenceDetector
    from autohedge.exchange_monitor import ExchangeMonitor
    from autohedge.dashboard_generator import TrustDashboard
    from autohedge.trader_interface import TraderQuestionnaire
except ImportError:
    logger.warning("Some enhanced features not available - check imports")
    SentimentPriceDivergenceDetector = None
    ExchangeMonitor = None
    TrustDashboard = None
    TraderQuestionnaire = None


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

DIRECTOR_PROMPT = """You are a Trading Director AI, responsible for orchestrating the trading process. 

Your primary objectives are:
1. Conduct in-depth market analysis to identify opportunities and challenges.
2. Develop comprehensive trading theses, encompassing both technical and fundamental aspects.
3. Collaborate with specialized agents to ensure a cohesive strategy.
4. Make informed, data-driven decisions on trade executions.

For each stock under consideration, please provide the following:

- A concise market thesis, outlining the overall market position and expected trends.
- Key technical and fundamental factors influencing the stock's performance.
- A detailed risk assessment, highlighting potential pitfalls and mitigation strategies.
- Trade parameters, including entry and exit points, position sizing, and risk management guidelines.

IMPORTANT: Consider all available data sources including:
- Market data and price action
- Technical indicators and patterns
- Sentiment analysis from news and social media
- Price divergences across exchanges
- Risk factors identified by other agents

Your analysis should be comprehensive, nuanced, and actionable.
"""

QUANT_PROMPT = """You are a Quantitative Analysis AI specializing in technical and statistical analysis of financial markets.

Your core responsibilities include:

1. **Technical Analysis**: Apply advanced technical indicators, chart patterns, and statistical methods to identify trading opportunities.

2. **Probability Assessment**: Calculate probability scores for different market scenarios and potential price movements.

3. **Volume Analysis**: Analyze trading volume patterns to confirm price movements and identify institutional activity.

4. **Volatility Analysis**: Assess market volatility and its implications for position sizing and risk management.

5. **Trend Identification**: Determine the strength and sustainability of market trends using multiple timeframe analysis.

For each analysis, you will receive:
- Stock ticker symbol
- Market thesis from the Trading Director
- Current market data and historical price information

Your output should include:

1. **Technical Indicators**: Key technical signals (RSI, MACD, moving averages, etc.)

2. **Support/Resistance Levels**: Critical price levels that may influence future price action

3. **Trend Analysis**: Current trend direction, strength, and potential reversal points

4. **Volume Profile**: Analysis of volume patterns and institutional activity

5. **Probability Assessment**: Likelihood of various price scenarios

6. **Risk/Reward Analysis**: Expected risk/reward ratios for potential trades

Provide specific, quantitative analysis that can be used for systematic trading decisions.
"""

RISK_PROMPT = """You are a Risk Assessment AI. Your primary objective is to evaluate and mitigate potential risks associated with trading strategies.

Your responsibilities include:

1. **Position Sizing**: Determine optimal capital allocation using risk-based methodologies (Kelly Criterion, fixed fractional, volatility-based).

2. **Drawdown Analysis**: Calculate potential maximum drawdown scenarios and establish acceptable risk thresholds.

3. **Market Risk Exposure**: Assess systematic and unsystematic risk factors affecting the trade.

4. **Correlation Analysis**: Monitor correlation risks across portfolio positions.

5. **Volatility Assessment**: Evaluate price volatility and its impact on position sizing.

6. **Risk Factor Integration**: Consider all risk signals including:
   - Technical risk factors
   - Sentiment-price divergences
   - Exchange data quality issues
   - Market liquidity conditions
   - News catalyst risks

For each trade, you will receive:
- Stock ticker and current price
- Trading thesis from Director
- Quantitative analysis from Quant Analyst
- Divergence alerts (if any)
- Exchange monitoring data (if available)

Your output must include:

1. **Recommended Position Size**: Specific dollar amount or percentage of capital

2. **Maximum Drawdown Risk**: Expected worst-case scenario

3. **Stop Loss Level**: Specific price level for risk management

4. **Take Profit Targets**: Multiple profit-taking levels

5. **Overall Risk Score**: 0-10 scale assessment

6. **Risk Mitigation Strategies**: Specific actions to reduce risk

Be conservative in risk assessment. Better to miss an opportunity than to take excessive risk.
"""

EXECUTION_PROMPT = """You are a Trade Execution AI. Your primary objective is to execute trades with precision and accuracy.

Your key responsibilities include:

1. **Generating structured order parameters**: Define the essential details of the trade.

2. **Setting precise entry/exit levels**: Determine exact entry and exit points based on technical analysis and market conditions.

3. **Determining order types**: Choose the most suitable order type (market, limit, stop-loss, trailing stop) based on market conditions.

4. **Specifying time constraints**: Define timeframe and time-in-force parameters.

5. **Slippage Considerations**: Account for expected slippage and adjust orders accordingly.

To execute trades effectively, provide exact trade execution details in a structured format:

**Required Order Details**:
- Stock symbol and quantity
- Entry price (specific or range)
- Stop loss price (mandatory for all trades)
- Take profit levels (at least 2 levels)
- Order type (market/limit/stop-limit)
- Time constraints (good-til-cancelled, day order, etc.)
- Execution strategy (aggressive/passive/TWAP/VWAP)

Consider:
- Current bid/ask spread
- Market liquidity and volume
- Time of day and market conditions
- Potential slippage

By following these guidelines, you will ensure that trades are executed efficiently, minimizing potential losses and maximizing profit opportunities.
"""

SENTIMENT_PROMPT = """You are a specialized Sentiment Analysis AI for financial markets.

Your core responsibilities:

1. **Sentiment Scoring**: Quantify market sentiment on a 0-1 scale where:
   - 0 = Extremely Negative
   - 0.5 = Neutral  
   - 1 = Extremely Positive

2. **Multi-Source Analysis**: Analyze sentiment from:
   - Financial news articles (Bloomberg, WSJ, Reuters, etc.)
   - Social media (Twitter/X, Reddit, StockTwits)
   - Analyst reports and institutional commentary
   - Company press releases and earnings calls

3. **Entity Recognition**: Identify specific companies, products, executives, and events mentioned.

4. **Theme Identification**: Extract key themes and narratives:
   - Product launches and innovations
   - Regulatory concerns and legal issues
   - Competitive dynamics and market share
   - Macroeconomic factors and sector trends
   - Earnings results and guidance
   - Management changes

5. **Sentiment Change Detection**: Identify significant shifts in sentiment that could signal changing market perception.

6. **Contrarian Indicator Assessment**: Evaluate when extreme sentiment might represent a contrarian trading opportunity.

For each analysis, provide:

1. **Overall Sentiment Score**: Aggregate sentiment (0-1 scale)

2. **Sentiment Breakdown**:
   - News Sentiment: Professional media analysis
   - Social Sentiment: Retail investor mood
   - Institutional Sentiment: Analyst and fund commentary

3. **Key Themes**: Primary narratives (both positive and negative)

4. **Critical Events**: Specific news events significantly impacting sentiment

5. **Sentiment Trend**: Whether sentiment is improving, deteriorating, or stable

6. **Contrarian Signals**: Indications of extreme sentiment that may reverse

7. **Confidence Level**: How reliable the sentiment reading is based on data quality

Your analysis should be data-driven, nuanced, and avoid simplistic conclusions. Recognize that sentiment is just one factor in market dynamics.
"""


# ============================================================================
# DATA MODELS
# ============================================================================

class AutoHedgeOutput(BaseModel):
    """Output model for individual stock analysis"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    thesis: Optional[str] = None
    quant_analysis: Optional[str] = None
    sentiment_analysis: Optional[str] = None
    divergence_alert: Optional[Dict] = None
    risk_assessment: Optional[str] = None
    order: Optional[str] = None
    decision: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    current_stock: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "current_stock": "NVDA",
                "thesis": "Strong AI demand driving growth",
                "confidence_score": 0.85,
                "decision": "BUY"
            }
        }


class AutoHedgeOutputMain(BaseModel):
    """Main output model aggregating all analyses"""
    name: Optional[str] = None
    description: Optional[str] = None
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    stocks: Optional[List[str]] = None
    task: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    logs: List[AutoHedgeOutput] = Field(default_factory=list)
    overall_confidence: Optional[float] = None
    risk_factors: Optional[List[Dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tech Portfolio Analysis",
                "stocks": ["NVDA", "AAPL"],
                "overall_confidence": 0.78,
                "logs": []
            }
        }


# ============================================================================
# AGENT CLASSES
# ============================================================================

class TradingDirector:
    """
    Trading Director Agent responsible for generating trading theses and coordinating strategy.
    
    Attributes:
        director_agent (Agent): Swarms agent for thesis generation
        tickr (TickrAgent): Agent for market data collection
    
    Methods:
        generate_thesis: Generates trading thesis for a given stock
        make_decision: Makes final go/no-go trading decision
    """
    
    def __init__(self, stocks: List[str], output_dir: str = "outputs"):
        logger.info("Initializing Trading Director")
        
        self.director_agent = Agent(
            agent_name="Trading-Director",
            system_prompt=DIRECTOR_PROMPT,
            model_name="anthropic/sonnet-3",
            output_type="str",
            max_loops=1,
            verbose=True,
            context_length=16000,
        )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_thesis(
        self, 
        task: str, 
        stock: str,
        additional_context: str = ""
    ) -> Tuple[str, str]:
        """
        Generate trading thesis for a given stock.
        
        Args:
            task: Trading task description
            stock: Stock ticker symbol
            additional_context: Extra context from other agents
        
        Returns:
            Tuple of (thesis, market_data)
        """
        logger.info(f"Generating thesis for {stock}")

        try:
            # Lazy import to avoid initialization at module load time
            from tickr_agent.main import TickrAgent

            # Initialize market data collector
            self.tickr = TickrAgent(
                stocks=[stock],
                max_loops=1,
                workers=10,
                retry_attempts=1,
                context_length=16000,
            )
            
            # Fetch market data
            market_data = self.tickr.run(
                f"{task} Analyze current market conditions and key metrics for {stock}"
            )
            
            # Construct comprehensive prompt
            prompt = f"""
            Task: {task}
            
            Stock: {stock}
            
            Market Data: {market_data}
            
            {additional_context}
            
            Generate a comprehensive trading thesis that integrates all available information.
            """
            
            # Generate thesis
            thesis = self.director_agent.run(prompt)
            
            return thesis, market_data
            
        except Exception as e:
            logger.error(f"Error generating thesis for {stock}: {str(e)}")
            raise
    
    def make_decision(
        self, 
        task: str, 
        thesis: str,
        all_analysis: str
    ) -> str:
        """
        Make final trading decision based on all available analysis.
        
        Args:
            task: Original trading task
            thesis: Generated thesis
            all_analysis: Compiled analysis from all agents
        
        Returns:
            Final decision (BUY/SELL/HOLD with reasoning)
        """
        prompt = f"""
        Based on the following comprehensive analysis, make a final trading decision.
        
        Original Task: {task}
        
        Thesis: {thesis}
        
        Complete Analysis:
        {all_analysis}
        
        Provide a clear decision: BUY, SELL, or HOLD with detailed reasoning.
        Include confidence level (0-100%) and key factors influencing the decision.
        """
        
        decision = self.director_agent.run(prompt)
        return decision


class QuantAnalyst:
    """
    Quantitative Analysis Agent responsible for technical and statistical analysis.
    
    Attributes:
        quant_agent (Agent): Swarms agent for analysis
    """
    
    def __init__(self):
        logger.info("Initializing Quant Analyst")
        
        self.quant_agent = Agent(
            agent_name="Quant-Analyst",
            system_prompt=QUANT_PROMPT,
            model_name="anthropic/sonnet-3",
            output_type="str",
            max_loops=1,
            verbose=True,
            context_length=16000,
        )
    
    def analyze(self, stock: str, thesis: str, market_data: str = "") -> str:
        """
        Perform quantitative analysis for a stock.
        
        Args:
            stock: Stock ticker symbol
            thesis: Trading thesis from Director
            market_data: Current market data
        
        Returns:
            Quantitative analysis report
        """
        logger.info(f"Performing quant analysis for {stock}")
        
        try:
            prompt = f"""
            Stock: {stock}
            
            Market Data: {market_data}
            
            Thesis from Trading Director: {thesis}
            
            Perform comprehensive quantitative analysis including:
            - Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
            - Support and resistance levels
            - Trend analysis and strength
            - Volume analysis
            - Probability assessment for different scenarios
            - Key technical levels
            
            Provide specific, actionable analysis with numerical values where possible.
            """
            
            analysis = self.quant_agent.run(prompt)
            return analysis
            
        except Exception as e:
            logger.error(f"Error in quant analysis for {stock}: {str(e)}")
            raise


class RiskManager:
    """
    Risk Management Agent responsible for position sizing and risk assessment.
    
    Attributes:
        risk_agent (Agent): Swarms agent for risk analysis
    """
    
    def __init__(self):
        logger.info("Initializing Risk Manager")
        
        self.risk_agent = Agent(
            agent_name="Risk-Manager",
            system_prompt=RISK_PROMPT,
            model_name="anthropic/sonnet-3",
            output_type="str",
            max_loops=1,
            verbose=True,
            context_length=16000,
        )
    
    def assess_risk(
        self, 
        stock: str, 
        thesis: str, 
        quant_analysis: str,
        market_data: str = "",
        divergence_data: Dict = None,
        exchange_data: Dict = None
    ) -> str:
        """
        Perform comprehensive risk assessment.
        
        Args:
            stock: Stock ticker
            thesis: Trading thesis
            quant_analysis: Technical analysis
            market_data: Current market data
            divergence_data: Sentiment-price divergence info
            exchange_data: Multi-exchange monitoring data
        
        Returns:
            Risk assessment report
        """
        logger.info(f"Assessing risk for {stock}")
        
        try:
            # Build comprehensive risk prompt
            prompt = f"""
            Stock: {stock}
            
            Market Data: {market_data}
            
            Thesis: {thesis}
            
            Quant Analysis: {quant_analysis}
            """
            
            # Add divergence alert if present
            if divergence_data and divergence_data.get('has_divergence'):
                prompt += f"""
                
                ⚠️ DIVERGENCE ALERT:
                Type: {divergence_data.get('divergence_type')}
                Severity: {divergence_data.get('severity')}
                Explanation: {divergence_data.get('explanation')}
                
                This divergence must be factored into risk assessment.
                """
            
            # Add exchange monitoring data if present
            if exchange_data:
                prompt += f"""
                
                Exchange Monitoring Data:
                Trust Scores: {exchange_data.get('trust_scores', {})}
                Price Spread: {exchange_data.get('spread_percent', 0):.2f}%
                Risk Factors: {exchange_data.get('risk_factors', [])}
                """
            
            prompt += """
            
            Provide comprehensive risk assessment including:
            1. Recommended position size (as % of portfolio)
            2. Maximum acceptable drawdown
            3. Stop loss level (specific price)
            4. Take profit targets (at least 2 levels)
            5. Overall risk score (0-10)
            6. Key risk factors and mitigation strategies
            
            Be conservative in your assessment.
            """
            
            assessment = self.risk_agent.run(prompt)
            return assessment
            
        except Exception as e:
            logger.error(f"Error in risk assessment for {stock}: {str(e)}")
            raise


class ExecutionAgent:
    """
    Trade Execution Agent responsible for generating trade orders.
    
    Attributes:
        execution_agent (Agent): Swarms agent for order generation
    """
    
    def __init__(self):
        logger.info("Initializing Execution Agent")
        
        self.execution_agent = Agent(
            agent_name="Execution-Agent",
            system_prompt=EXECUTION_PROMPT,
            model_name="anthropic/sonnet-3",
            output_type="str",
            max_loops=1,
            verbose=True,
            context_length=16000,
        )
    
    def generate_order(
        self, 
        stock: str, 
        thesis: str, 
        risk_assessment: str,
        market_data: str = ""
    ) -> str:
        """
        Generate trade order with specific parameters.
        
        Args:
            stock: Stock ticker
            thesis: Trading thesis
            risk_assessment: Risk analysis
            market_data: Current market data
        
        Returns:
            Structured trade order
        """
        logger.info(f"Generating trade order for {stock}")
        
        try:
            prompt = f"""
            Stock: {stock}
            
            Market Data: {market_data}
            
            Thesis: {thesis}
            
            Risk Assessment: {risk_assessment}
            
            Generate a complete trade order including:
            1. Order type (market/limit/stop-limit)
            2. Quantity (based on risk assessment)
            3. Entry price (or price range for limit orders)
            4. Stop loss price (mandatory)
            5. Take profit levels (at least 2)
            6. Time in force (GTC, Day, etc.)
            7. Execution strategy (aggressive/passive/TWAP)
            
            Consider current market conditions, liquidity, and bid/ask spread.
            Provide specific, executable order parameters.
            """
            
            order = self.execution_agent.run(prompt)
            return order
            
        except Exception as e:
            logger.error(f"Error generating order for {stock}: {str(e)}")
            raise


class SentimentAgent:
    """
    Sentiment Analysis Agent for news and social media analysis.
    
    Attributes:
        sentiment_agent (Agent): Swarms agent for sentiment analysis
    """
    
    def __init__(self):
        logger.info("Initializing Sentiment Agent")
        
        self.sentiment_agent = Agent(
            agent_name="Sentiment-Agent",
            system_prompt=SENTIMENT_PROMPT,
            model_name="gpt-4o-mini",
            output_type="str",
            max_loops=1,
            verbose=True,
            context_length=16000,
        )
    
    def analyze_sentiment(self, stock: str, news_data: str) -> str:
        """
        Analyze market sentiment from news and social media.
        
        Args:
            stock: Stock ticker
            news_data: News articles and social media posts
        
        Returns:
            Sentiment analysis report
        """
        logger.info(f"Analyzing sentiment for {stock}")
        
        try:
            prompt = f"""
            Stock: {stock}
            
            News and Social Media Data:
            {news_data}
            
            Provide comprehensive sentiment analysis including:
            1. Overall sentiment score (0-1)
            2. Sentiment breakdown (news vs social vs institutional)
            3. Key themes identified
            4. Critical events impacting sentiment
            5. Sentiment trend (improving/deteriorating/stable)
            6. Contrarian signals (if any)
            7. Confidence in sentiment reading
            """
            
            analysis = self.sentiment_agent.run(prompt)
            return analysis
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {stock}: {str(e)}")
            return "Sentiment analysis unavailable"


# ============================================================================
# MAIN AUTOHEDGE CLASS
# ============================================================================

class AutoHedge:
    """
    Main trading system that coordinates all agents and manages the trading cycle.
    
    This is the primary class users interact with. It orchestrates:
    - Data collection from multiple sources
    - Multi-agent analysis (Director, Quant, Risk, Execution, Sentiment)
    - Divergence detection
    - Exchange monitoring
    - Interactive trader feedback
    - Decision making and order generation
    
    Attributes:
        stocks (List[str]): List of stock tickers to trade
        name (str): Name of the trading system
        description (str): Description of trading strategy
        director (TradingDirector): Trading director agent
        quant (QuantAnalyst): Quantitative analysis agent
        risk (RiskManager): Risk management agent
        execution (ExecutionAgent): Trade execution agent
        sentiment (SentimentAgent): Sentiment analysis agent
        divergence_detector (SentimentPriceDivergenceDetector): Optional divergence detector
        exchange_monitor (ExchangeMonitor): Optional exchange monitor
        trader_interface (TraderQuestionnaire): Optional interactive Q&A
        output_dir (Path): Directory for storing outputs
        conversation (Conversation): Conversation context across agents
    """
    
    def __init__(
        self,
        stocks: List[str],
        name: str = "autohedge",
        description: str = "fully autonomous hedgefund",
        output_dir: str = "outputs",
        output_file_path: str = None,
        strategy: str = None,
        output_type: str = "list",
        enable_divergence_detection: bool = True,
        enable_exchange_monitoring: bool = False,
        enable_interactive_mode: bool = False,
        enable_sentiment_analysis: bool = True,
    ):
        """
        Initialize the AutoHedge trading system.
        
        Args:
            stocks: List of stock tickers to trade
            name: Name of the trading system
            description: Description of the trading strategy
            output_dir: Directory for storing outputs
            output_file_path: Path to output file
            strategy: Strategy name/type
            output_type: Output format ('list', 'dict', 'str')
            enable_divergence_detection: Enable sentiment-price divergence detection
            enable_exchange_monitoring: Enable multi-exchange monitoring
            enable_interactive_mode: Enable trader Q&A interface
            enable_sentiment_analysis: Enable news/social sentiment analysis
        """
        self.name = name
        self.description = description
        self.stocks = stocks
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.strategy = strategy
        self.output_type = output_type
        self.output_file_path = output_file_path
        
        # Feature flags
        self.enable_divergence_detection = enable_divergence_detection
        self.enable_exchange_monitoring = enable_exchange_monitoring
        self.enable_interactive_mode = enable_interactive_mode
        self.enable_sentiment_analysis = enable_sentiment_analysis
        
        logger.info("="*60)
        logger.info(f"Initializing AutoHedge Trading System: {name}")
        logger.info("="*60)
        
        # Initialize core agents
        logger.info("Initializing core agents...")
        self.director = TradingDirector(stocks, str(self.output_dir))
        self.quant = QuantAnalyst()
        self.risk = RiskManager()
        self.execution = ExecutionAgent()
        
        # Initialize optional agents
        if enable_sentiment_analysis:
            self.sentiment = SentimentAgent()
        else:
            self.sentiment = None
        
        # Initialize enhanced features
        if enable_divergence_detection and SentimentPriceDivergenceDetector:
            logger.info("Enabling divergence detection...")
            self.divergence_detector = SentimentPriceDivergenceDetector()
        else:
            self.divergence_detector = None
        
        if enable_exchange_monitoring and ExchangeMonitor:
            logger.info("Enabling exchange monitoring...")
            self.exchange_monitor = ExchangeMonitor()
        else:
            self.exchange_monitor = None
        
        if enable_interactive_mode and TraderQuestionnaire:
            logger.info("Enabling interactive trader interface...")
            self.trader_interface = TraderQuestionnaire()
        else:
            self.trader_interface = None
        
        # Initialize output structures
        self.logs = AutoHedgeOutputMain(
            name=self.name,
            description=self.description,
            stocks=stocks,
            task="",
            logs=[],
        )
        
        self.conversation = Conversation(time_enabled=True)
        
        # Tracking
        self.overall_confidence = 0.75  # Default confidence
        self.risk_factors = []
        self.trust_scores = {}
        
        logger.info("✅ AutoHedge initialized successfully")
        logger.info(f"   Stocks: {', '.join(stocks)}")
        logger.info(f"   Features enabled:")
        logger.info(f"     - Sentiment Analysis: {enable_sentiment_analysis}")
        logger.info(f"     - Divergence Detection: {enable_divergence_detection}")
        logger.info(f"     - Exchange Monitoring: {enable_exchange_monitoring}")
        logger.info(f"     - Interactive Mode: {enable_interactive_mode}")
        logger.info("="*60 + "\n")
    
    def run(self, task: str, *args, **kwargs) -> any:
        """
        Execute one complete trading cycle for all stocks.
        
        This is the main entry point that orchestrates the entire analysis workflow:
        1. Generate thesis for each stock
        2. Perform quantitative analysis
        3. Analyze sentiment (if enabled)
        4. Detect divergences (if enabled)
        5. Monitor exchanges (if enabled)
        6. Assess risks
        7. Generate trade orders
        8. Make final decision
        9. Interactive trader feedback (if enabled)
        
        Args:
            task: Trading task description
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        
        Returns:
            Trading analysis results in specified format (list/dict/str)
        """
        logger.info("\n" + "="*60)
        logger.info("STARTING TRADING CYCLE")
        logger.info("="*60)
        logger.info(f"Task: {task}")
        logger.info(f"Stocks: {', '.join(self.stocks)}")
        logger.info("="*60 + "\n")
        
        # Add task to conversation
        self.conversation.add(role="user", content=f"Task: {task}")
        self.logs.task = task
        
        try:
            # Process each stock
            for stock in self.stocks:
                logger.info(f"\n{'─'*60}")
                logger.info(f"Processing: {stock}")
                logger.info(f"{'─'*60}\n")
                
                stock_analysis = self._analyze_stock(task, stock)
                
                # Add to logs
                self.logs.logs.append(stock_analysis)
            
            # Calculate overall confidence
            self._calculate_overall_confidence()
            
            # Interactive mode
            if self.enable_interactive_mode and self.trader_interface:
                self._run_interactive_session()
            
            # Generate output
            return self._generate_output()
            
        except Exception as e:
            logger.error(f"❌ Trading cycle failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _analyze_stock(self, task: str, stock: str) -> AutoHedgeOutput:
        """
        Perform complete analysis for a single stock.
        
        Args:
            task: Trading task
            stock: Stock ticker
        
        Returns:
            AutoHedgeOutput with complete analysis
        """
        analysis_output = AutoHedgeOutput(current_stock=stock)
        additional_context = ""
        
        # Step 1: Check for divergences
        divergence_data = None
        if self.divergence_detector:
            logger.info(f"🔍 Checking for sentiment-price divergences...")
            try:
                divergence_data = self.divergence_detector.detect_divergence(stock)
                if divergence_data.get('has_divergence'):
                    logger.warning(f"⚠️ {divergence_data.get('divergence_type')} divergence detected!")
                    logger.warning(f"   {divergence_data.get('explanation')}")
                    
                    analysis_output.divergence_alert = divergence_data
                    additional_context += f"\n⚠️ DIVERGENCE ALERT: {divergence_data.get('explanation')}\n"
            except Exception as e:
                logger.warning(f"Divergence detection failed: {e}")
        
        # Step 2: Monitor exchanges
        exchange_data = None
        if self.exchange_monitor:
            logger.info(f"📊 Monitoring exchange data...")
            try:
                import asyncio
                prices = asyncio.run(self.exchange_monitor.fetch_all_prices(stock))
                spread = self.exchange_monitor.calculate_price_spread(prices)
                trust_scores = self.exchange_monitor.update_trust_scores(prices)
                risk_factors = self.exchange_monitor.get_risk_factors(prices, spread)
                
                exchange_data = {
                    'prices': prices,
                    'spread_percent': spread.get('spread_percent', 0),
                    'trust_scores': trust_scores,
                    'risk_factors': risk_factors
                }
                
                self.trust_scores = trust_scores
                self.risk_factors.extend(risk_factors)
                
                if risk_factors:
                    logger.warning(f"⚠️ Exchange risk factors detected:")
                    for rf in risk_factors:
                        logger.warning(f"   - {rf['message']}")
                
            except Exception as e:
                logger.warning(f"Exchange monitoring failed: {e}")
        
        # Step 3: Generate thesis
        logger.info(f"📝 Generating trading thesis...")
        thesis, market_data = self.director.generate_thesis(
            task=task, 
            stock=stock,
            additional_context=additional_context
        )
        
        analysis_output.thesis = thesis
        
        self.conversation.add(
            role=self.director.director_agent.agent_name,
            content=f"Stock: {stock}\nMarket Data: {market_data}\nThesis: {thesis}"
        )
        
        # Step 4: Quantitative analysis
        logger.info(f"📈 Performing quantitative analysis...")
        quant_analysis = self.quant.analyze(stock, thesis, market_data)
        
        analysis_output.quant_analysis = quant_analysis
        
        self.conversation.add(
            role=self.quant.quant_agent.agent_name,
            content=quant_analysis
        )
        
        # Step 5: Sentiment analysis (if enabled)
        sentiment_analysis = None
        if self.sentiment:
            logger.info(f"💭 Analyzing market sentiment...")
            try:
                # This would normally fetch real news data
                # For now, using a placeholder
                news_data = f"Recent news and social media data for {stock}"
                sentiment_analysis = self.sentiment.analyze_sentiment(stock, news_data)
                
                analysis_output.sentiment_analysis = sentiment_analysis
                
                self.conversation.add(
                    role=self.sentiment.sentiment_agent.agent_name,
                    content=sentiment_analysis
                )
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Step 6: Risk assessment
        logger.info(f"⚠️ Assessing risks...")
        risk_assessment = self.risk.assess_risk(
            stock=stock,
            thesis=thesis,
            quant_analysis=quant_analysis,
            market_data=market_data,
            divergence_data=divergence_data,
            exchange_data=exchange_data
        )
        
        analysis_output.risk_assessment = risk_assessment
        
        self.conversation.add(
            role=self.risk.risk_agent.agent_name,
            content=risk_assessment
        )
        
        # Step 7: Generate order
        logger.info(f"📋 Generating trade order...")
        order = self.execution.generate_order(
            stock=stock,
            thesis=thesis,
            risk_assessment=risk_assessment,
            market_data=market_data
        )
        
        analysis_output.order = order
        
        self.conversation.add(
            role=self.execution.execution_agent.agent_name,
            content=order
        )
        
        # Step 8: Final decision
        logger.info(f"🎯 Making final decision...")
        
        # Compile all analysis for decision making
        all_analysis = f"""
        Thesis: {thesis}
        
        Quant Analysis: {quant_analysis}
        
        {f"Sentiment Analysis: {sentiment_analysis}" if sentiment_analysis else ""}
        
        {f"Divergence Alert: {divergence_data.get('explanation')}" if divergence_data and divergence_data.get('has_divergence') else ""}
        
        Risk Assessment: {risk_assessment}
        
        Proposed Order: {order}
        """
        
        decision = self.director.make_decision(task, thesis, all_analysis)
        
        analysis_output.decision = decision
        
        self.conversation.add(
            role=self.director.director_agent.agent_name,
            content=f"Final Decision: {decision}"
        )
        
        logger.info(f"✅ Analysis complete for {stock}\n")
        
        return analysis_output
    
    def _calculate_overall_confidence(self):
        """Calculate overall confidence score based on all factors"""
        confidence = 0.75  # Base confidence
        
        # Adjust based on risk factors
        if len(self.risk_factors) > 3:
            confidence -= 0.15
        elif len(self.risk_factors) > 0:
            confidence -= 0.05
        
        # Adjust based on trust scores
        if self.trust_scores:
            avg_trust = sum(self.trust_scores.values()) / len(self.trust_scores)
            confidence = (confidence + avg_trust) / 2
        
        self.overall_confidence = max(0.0, min(1.0, confidence))
        self.logs.overall_confidence = self.overall_confidence
        self.logs.risk_factors = self.risk_factors
    
    def _run_interactive_session(self):
        """Run interactive Q&A session with trader"""
        logger.info("\n💬 Starting interactive trader session...")
        
        context = {
            'risk_factors': self.risk_factors,
            'trust_scores': self.trust_scores,
            'confidence': self.overall_confidence
        }
        
        questions = self.trader_interface.generate_questions_from_context(context)
        
        for question in questions[:3]:  # Limit to top 3 questions
            logger.info(f"\nQuestion: {question['question']}")
            # In production, this would await user input
            # For now, we'll skip actual interaction
    
    def _generate_output(self) -> any:
        """Generate output in specified format"""
        if self.output_type == "list":
            return self.conversation.return_messages_as_list()
        
        elif self.output_type == "dict":
            output_dict = self.conversation.return_messages_as_dictionary()
            output_dict['overall_confidence'] = self.overall_confidence
            output_dict['risk_factors'] = self.risk_factors
            return output_dict
        
        elif self.output_type == "str":
            return str(self.conversation)
        
        elif self.output_type == "json":
            output_file = self.output_file_path or f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.output_dir / output_file
            
            with open(output_path, 'w') as f:
                json.dump(self.logs.model_dump(), f, indent=2, default=str)
            
            logger.info(f"💾 Output saved to: {output_path}")
            
            return self.logs.model_dump_json(indent=2)
        
        else:
            return self.logs.model_dump_json(indent=2)
    
    def generate_dashboard(self) -> str:
        """Generate trust breakdown dashboard"""
        if not TrustDashboard:
            return "Dashboard generator not available"
        
        recommendations = []
        
        # Generate recommendations based on risk factors
        for rf in self.risk_factors[:3]:
            recommendations.append(f"✓ Address: {rf['message']}")
        
        if self.overall_confidence < 0.7:
            recommendations.append("✓ Consider waiting for better market conditions")
        
        dashboard = TrustDashboard.generate_dashboard(
            overall_confidence=self.overall_confidence,
            trust_scores=self.trust_scores if self.trust_scores else {'primary_data': 0.85},
            risk_factors=self.risk_factors,
            recommendations=recommendations if recommendations else ["✓ All systems nominal"],
            divergence_data=None  # Would be populated from analysis
        )
        
        return dashboard


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Basic usage
    from dotenv import load_dotenv
    load_dotenv()
    
    # Define stocks
    stocks = ["NVDA"]
    
    # Initialize system
    trading_system = AutoHedge(
        stocks=stocks,
        name="AI-Tech-Fund",
        description="AI and technology focused trading",
        enable_divergence_detection=True,
        enable_sentiment_analysis=True,
        output_type="dict"
    )
    
    # Define task
    task = "Analyze NVIDIA for potential investment with $50,000 allocation, focusing on AI market trends"
    
    # Run analysis
    result = trading_system.run(task=task)
    
    # Display results
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Overall Confidence: {trading_system.overall_confidence:.2%}")
    print(f"Risk Factors: {len(trading_system.risk_factors)}")
    
    # Generate dashboard
    if trading_system.trust_scores:
        print("\n" + trading_system.generate_dashboard())