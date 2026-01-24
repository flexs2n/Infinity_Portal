"""
Backtest API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from autohedge.backtest.backtest_engine import BacktestEngine

router = APIRouter(prefix="/backtests", tags=["Backtesting"])


class BacktestRequest(BaseModel):
    strategy_code: str
    ticker: str
    years: int = 5
    initial_capital: float = 100000


@router.post("/run", response_model=Dict)
async def run_backtest(request: BacktestRequest):
    """
    Run backtest for a strategy
    """
    try:
        engine = BacktestEngine()
        
        results = engine.run_backtest(
            algorithm_code=request.strategy_code,
            ticker=request.ticker,
            years=request.years,
            initial_capital=request.initial_capital
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_strategies(strategy_codes: List[str], ticker: str):
    """
    Compare multiple strategies
    """
    # Implementation for multi-strategy comparison
    return {
        "message": "Strategy comparison coming soon",
        "strategies_count": len(strategy_codes)
    }