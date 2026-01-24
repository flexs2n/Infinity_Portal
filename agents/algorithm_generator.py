from swarms import Agent
from swarm_models import Anthropic ClaudeModel
from typing import Dict, List
from loguru import logger
import os

class AlgorithmGeneratorAgent:
    """
    AI agent that writes Python trading algorithms based on discovered edges
    Uses Claude (better at code generation than GPT-4)
    """
    
    def __init__(self):
        self.model = AnthropicClaudeModel(
            model_name="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3  # Lower for precise code generation
        )
        
        self.agent = Agent(
            agent_name="Algorithm-Generator",
            system_prompt=self._get_system_prompt(),
            llm=self.model,
            max_loops=2,
            autosave=True,
            verbose=True,
            context_length=200000,  # Claude's 200k context
            output_type="str"  # Returns Python code
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert quantitative trading algorithm developer.

Your job is to convert trading edge descriptions into executable Python algorithms compatible with backtesting frameworks.

REQUIREMENTS:
1. Use vectorbt Pro framework for backtesting (fast, professional-grade)
2. Include proper risk management (position sizing, stop losses)
3. Handle edge cases and data quality issues
4. Include detailed comments explaining logic
5. Make algorithms modifiable/parameterizable

ALGORITHM STRUCTURE:
```python
import vectorbt as vbt
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class [StrategyName]Strategy:
    \"\"\"
    Strategy Description
    
    Edge: [Edge description]
    Entry: [Entry conditions]
    Exit: [Exit conditions]
    \"\"\"
    
    def __init__(self, params: Dict):
        self.params = params
        # Parameters like thresholds, windows, etc.
    
    def generate_signals(
        self, 
        price_data: pd.DataFrame,
        social_data: pd.DataFrame,
        news_data: pd.DataFrame
    ) -> Tuple[pd.Series, pd.Series]:
        \"\"\"
        Generate entry and exit signals
        
        Returns:
            (entries, exits) - Boolean Series
        \"\"\"
        # Implementation
        pass
    
    def calculate_position_size(
        self,
        capital: float,
        price: float,
        volatility: float
    ) -> float:
        \"\"\"Risk-based position sizing\"\"\"
        # Kelly Criterion or volatility-based sizing
        pass