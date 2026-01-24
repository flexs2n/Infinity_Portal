# infinity_portal/agents/strategy_optimizer.py (NEW FILE)

from swarms import Agent
from swarm_models import AnthropicClaudeModel
from typing import Dict
from loguru import logger
import os

class StrategyOptimizerAgent:
    """
    AI agent that modifies trading algorithms based on backtest results
    Iteratively improves strategies
    """
    
    def __init__(self):
        self.model = AnthropicClaudeModel(
            model_name="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.4
        )
        
        self.agent = Agent(
            agent_name="Strategy-Optimizer",
            system_prompt=self._get_system_prompt(),
            llm=self.model,
            max_loops=1,
            autosave=True,
            verbose=True,
            context_length=200000
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert trading strategy optimizer.

Your job is to analyze backtest results and modify trading algorithms to improve performance.

OPTIMIZATION GOALS (in order of priority):
1. Risk-Adjusted Returns (Sharpe Ratio > 2.0)
2. Drawdown Control (Max DD < 15%)
3. Consistency (Win Rate > 55%)
4. Total Returns (Beat S&P500)

COMMON ISSUES AND FIXES:
- Low Sharpe → Tighten entry conditions, improve risk management
- High Drawdown → Add stop losses, reduce position sizing
- Low Win Rate → Refine entry signals, avoid false signals
- Underperformance vs Benchmark → Increase conviction, use leverage wisely

MODIFICATION TECHNIQUES:
1. **Parameter Tuning**: Adjust thresholds, windows, etc.
2. **Signal Refinement**: Add filters to reduce false positives
3. **Risk Management**: Improve position sizing and stop losses
4. **Regime Filtering**: Add market condition filters
5. **Exit Optimization**: Improve profit-taking and loss-cutting

OUTPUT: Complete modified algorithm code with explanation of changes.
"""
    
    def optimize_strategy(
        self,
        original_code: str,
        backtest_results: Dict,
        optimization_target: str = "sharpe"
    ) -> Dict:
        """
        Optimize strategy based on backtest results
        
        Args:
            original_code: Current algorithm code
            backtest_results: Performance metrics
            optimization_target: What to optimize for
        
        Returns:
            {
                'optimized_code': str,
                'changes_made': list,
                'expected_improvement': dict
            }
        """
        logger.info(f"🔧 Optimizing strategy (target: {optimization_target})...")
        
        # Identify issues
        issues = self._identify_issues(backtest_results)
        
        optimization_prompt = f"""
OPTIMIZE THE FOLLOWING TRADING ALGORITHM:

CURRENT PERFORMANCE:
- Total Return: {backtest_results.get('total_return', 'N/A'):.2f}%
- Sharpe Ratio: {backtest_results.get('sharpe_ratio', 'N/A'):.2f}
- Max Drawdown: {backtest_results.get('max_drawdown', 'N/A'):.2f}%
- Win Rate: {backtest_results.get('win_rate', 'N/A'):.2f}%

S&P500 COMPARISON:
- S&P500 Return: {backtest_results.get('benchmark_comparison', {}).get('sp500_return', 'N/A'):.2f}%
- Alpha: {backtest_results.get('benchmark_comparison', {}).get('alpha', 'N/A'):.2f}%
- Beta: {backtest_results.get('benchmark_comparison', {}).get('beta', 'N/A'):.2f}

IDENTIFIED ISSUES:
{chr(10).join(f"- {issue}" for issue in issues)}

CURRENT ALGORITHM CODE:
```python
{original_code}