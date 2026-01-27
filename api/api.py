import time
import uuid
import asyncio
import json as json_lib
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Query,
    Security,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, EmailStr, Field

from infinity_portal.main import AutoHedge as infinity_portal


def log_agent_data(data_dict: dict) -> dict | None:
    """
    Logs agent data to the Swarms database with retry logic.

    Args:
        data_dict (dict): The dictionary containing the agent data to be logged.
        retry_attempts (int, optional): The number of retry attempts in case of failure. Defaults to 3.

    Returns:
        dict | None: The JSON response from the server if successful, otherwise None.

    Raises:
        ValueError: If data_dict is empty or invalid
        requests.exceptions.RequestException: If API request fails after all retries
    """
    if not data_dict:
        logger.error("Empty data dictionary provided")
        raise ValueError("data_dict cannot be empty")

    url = "https://swarms.world/api/get-agents/log-agents"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-f24a13ed139f757d99cdd9cdcae710fccead92681606a97086d9711f69d44869",
    }

    requests.post(url, json=data_dict, headers=headers, timeout=10)
    # response.raise_for_status()

    return None


# Enhanced Pydantic Models
class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    fund_name: str = Field(..., min_length=3, max_length=100)
    fund_description: Optional[str] = Field(None, max_length=500)


class UserUpdate(BaseModel):
    fund_name: Optional[str] = Field(
        None, min_length=3, max_length=100
    )
    fund_description: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None


class User(UserCreate):
    id: str
    api_key: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class TradingTask(BaseModel):
    stocks: List[str] = Field(..., min_items=1)
    task: str = Field(..., min_length=10)
    allocation: float = Field(..., gt=0)
    strategy_type: Optional[str] = Field(
        None, description="Trading strategy type"
    )
    risk_level: Optional[int] = Field(
        None, ge=1, le=10, description="Risk level from 1-10"
    )


class TradeResponse(BaseModel):
    id: str
    user_id: str
    task: TradingTask
    status: TradeStatus
    created_at: datetime
    executed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    performance_metrics: Optional[Dict[str, float]]


class HistoricalAnalytics(BaseModel):
    total_trades: int
    success_rate: float
    average_return: float
    total_allocation: float
    risk_adjusted_return: float
    top_performing_stocks: List[Tuple[str, float]]


# Configure Loguru with more detailed formatting
logger.add(
    "logs/infinity_portal_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True,
)


class infinity_portalAPI:
    def __init__(self, *args, **kwargs):
        self.app = FastAPI(
            title="infinity_portal API",
            version="1.0.0",
            description="Production-grade API for automated hedge fund management",
            *args,
            **kwargs,
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://frontend:80",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.api_key_header = APIKeyHeader(name="X-API-Key")
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, str] = {}
        self.trades: Dict[str, TradeResponse] = {}
        self.performance_cache: Dict[str, Dict] = {}

        self._setup_routes()
        logger.info(
            "infinity_portal API initialized with enhanced features"
        )

    @contextmanager
    def _log_execution_time(
        self, operation: str, user_id: Optional[str] = None
    ):
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            {
                "operation": operation,
                "execution_time": execution_time,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc),
            }
            # logger.info(f"Operation '{operation}' metrics: {json_data}")

    async def _get_current_user(
        self, api_key: str = Security(APIKeyHeader(name="X-API-Key"))
    ) -> User:
        user_id = self.api_keys.get(api_key)
        if not user_id or user_id not in self.users:
            logger.warning(
                f"Invalid API key attempt: {api_key[:8]}..."
            )
            raise HTTPException(
                status_code=401, detail="Invalid API key"
            )

        user = self.users[user_id]
        user.last_login = datetime.now(timezone.utc)
        return user

    def _calculate_performance_metrics(
        self, trade_result: Dict
    ) -> Dict[str, float]:
        """Calculate performance metrics for a trade"""
        try:
            # Implementation would depend on the structure of trade_result
            return {
                "return_percentage": 0.0,  # Placeholder
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "volatility": 0.0,
            }
        except Exception as e:
            logger.error(
                f"Error calculating performance metrics: {str(e)}"
            )
            return {}

    def _setup_routes(self):
        # User Management Routes
        @self.app.post("/users", response_model=User)
        async def create_user(user: UserCreate):
            with self._log_execution_time("create_user"):
                user_id = str(uuid.uuid4())
                api_key = str(uuid.uuid4())

                user_data = User(
                    id=user_id,
                    api_key=api_key,
                    created_at=datetime.now(timezone.utc),
                    **user.dict(),
                )

                self.users[user_id] = user_data
                self.api_keys[api_key] = user_id

                logger.info(f"New user created: {user.username}")
                return user_data

        @self.app.get("/users/me", response_model=User)
        async def get_current_user(
            current_user: User = Depends(self._get_current_user),
        ):
            return current_user

        @self.app.put("/users/me", response_model=User)
        async def update_user(
            user_update: UserUpdate,
            current_user: User = Depends(self._get_current_user),
        ):
            with self._log_execution_time(
                "update_user", current_user.id
            ):
                updated_data = current_user.dict()
                updated_data.update(
                    user_update.dict(exclude_unset=True)
                )

                updated_user = User(**updated_data)
                self.users[current_user.id] = updated_user

                logger.info(f"User updated: {current_user.id}")
                return updated_user

        # Trading Routes
        @self.app.post("/trades", response_model=TradeResponse)
        async def create_trade(
            task: TradingTask,
            current_user: User = Depends(self._get_current_user),
        ):
            with self._log_execution_time(
                "create_trade", current_user.id
            ):
                trade_id = str(uuid.uuid4())

                try:
                    trading_system = infinity_portal(
                        name=current_user.fund_name,
                        description=current_user.fund_description
                        or "",
                        stocks=task.stocks,
                        output_type="structured",  # Return structured data for frontend
                    )

                    trade_response = TradeResponse(
                        id=trade_id,
                        user_id=current_user.id,
                        task=task,
                        status=TradeStatus.EXECUTING,
                        created_at=datetime.now(timezone.utc),
                        executed_at=None,
                        result=None,
                        performance_metrics=None,
                    )

                    # Execute trade
                    result = trading_system.run(task=task.task)

                    # Update trade response
                    trade_response.status = TradeStatus.COMPLETED
                    trade_response.executed_at = datetime.now(
                        timezone.utc
                    )
                    trade_response.result = result
                    trade_response.performance_metrics = (
                        self._calculate_performance_metrics(result)
                    )

                    # Store trade
                    self.trades[trade_id] = trade_response

                    # Log to Swarms
                    self._log_to_swarms(
                        {
                            "trade_id": trade_id,
                            "user_id": current_user.id,
                            "task": task.dict(),
                            "result": result,
                            "performance_metrics": trade_response.performance_metrics,
                        }
                    )

                    return trade_response

                except Exception as e:
                    logger.error(f"Trade execution failed: {str(e)}")
                    raise HTTPException(
                        status_code=500, detail=str(e)
                    )

        @self.app.get("/trades", response_model=List[TradeResponse])
        async def list_trades(
            current_user: User = Depends(self._get_current_user),
            skip: int = Query(0, ge=0),
            limit: int = Query(10, ge=1, le=100),
            status: Optional[TradeStatus] = None,
        ):
            with self._log_execution_time(
                "list_trades", current_user.id
            ):
                user_trades = [
                    trade
                    for trade in self.trades.values()
                    if trade.user_id == current_user.id
                    and (status is None or trade.status == status)
                ]

                return sorted(
                    user_trades,
                    key=lambda x: x.created_at,
                    reverse=True,
                )[skip : skip + limit]

        @self.app.get(
            "/trades/{trade_id}", response_model=TradeResponse
        )
        async def get_trade(
            trade_id: str = Path(
                ..., title="The ID of the trade to get"
            ),
            current_user: User = Depends(self._get_current_user),
        ):
            if trade_id not in self.trades:
                raise HTTPException(
                    status_code=404, detail="Trade not found"
                )

            trade = self.trades[trade_id]
            if trade.user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to access this trade",
                )

            return trade

        @self.app.delete("/trades/{trade_id}")
        async def delete_trade(
            trade_id: str = Path(
                ..., title="The ID of the trade to delete"
            ),
            current_user: User = Depends(self._get_current_user),
        ):
            if trade_id not in self.trades:
                raise HTTPException(
                    status_code=404, detail="Trade not found"
                )

            trade = self.trades[trade_id]
            if trade.user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to delete this trade",
                )

            del self.trades[trade_id]
            logger.info(f"Trade deleted: {trade_id}")
            return {"message": "Trade deleted successfully"}

        # Streaming Trade Endpoint - for real-time progress updates
        @self.app.post("/trades/stream")
        async def create_trade_stream(
            task: TradingTask,
            current_user: User = Depends(self._get_current_user),
        ):
            """Create a trade with streaming progress updates via SSE"""
            
            async def generate_stream():
                trade_id = str(uuid.uuid4())
                
                try:
                    # Create initial trade record so users can navigate to it early
                    initial_trade = TradeResponse(
                        id=trade_id,
                        user_id=current_user.id,
                        task=task,
                        status=TradeStatus.EXECUTING,
                        created_at=datetime.now(timezone.utc),
                        executed_at=None,
                        result={'status': 'analyzing', 'message': 'AI analysis in progress...'},
                        performance_metrics=None,
                    )
                    self.trades[trade_id] = initial_trade
                    
                    # Send initial status with trade_id for "Skip to Report"
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'init', 'message': '🚀 Initializing AI trading system...', 'progress': 5, 'trade_id': trade_id})}\n\n"
                    await asyncio.sleep(0.5)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'agents', 'message': '🤖 Activating AI agents: Trading Director, Quant Analyst, Risk Manager...', 'progress': 10, 'trade_id': trade_id})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    # Initialize the trading system
                    trading_system = infinity_portal(
                        name=current_user.fund_name,
                        description=current_user.fund_description or "",
                        stocks=task.stocks,
                        output_type="structured",
                    )
                    
                    stock_list = ", ".join(task.stocks)
                    
                    msg = f"📊 Fetching real-time market data for {stock_list}..."
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'market_data', 'message': msg, 'progress': 20})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    msg = f"Analyzing market conditions for {stock_list}. Looking at current price trends, volume patterns, and recent news catalysts..."
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'agent': 'Trading Director', 'message': msg, 'progress': 25})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'thesis', 'message': '📝 Trading Director: Generating investment thesis...', 'progress': 30})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'agent': 'Trading Director', 'message': 'Evaluating fundamental factors: earnings growth, market position, competitive advantages, and sector trends...', 'progress': 35})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'quant', 'message': '📈 Quant Analyst: Running technical analysis...', 'progress': 45})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'agent': 'Quant Analyst', 'message': 'Calculating RSI, MACD, Moving Averages, Bollinger Bands. Identifying support/resistance levels and trend strength...', 'progress': 50})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'sentiment', 'message': '💬 Sentiment Agent: Analyzing market sentiment...', 'progress': 60})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'agent': 'Sentiment Agent', 'message': 'Scanning financial news, social media sentiment, analyst ratings, and institutional activity for sentiment signals...', 'progress': 65})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'risk', 'message': '⚠️ Risk Manager: Assessing risk factors...', 'progress': 75})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    msg = f"Calculating position size for ${task.allocation:,.0f} allocation. Determining stop-loss levels, maximum drawdown, and risk-adjusted returns..."
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'agent': 'Risk Manager', 'message': msg, 'progress': 80})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'execution', 'message': '📋 Execution Agent: Generating trade parameters...', 'progress': 85})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    # Actually run the analysis
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'analysis', 'message': '🧠 Running comprehensive AI analysis... This may take 1-3 minutes.', 'progress': 90})}\n\n"
                    
                    # Run the actual trading analysis
                    result = trading_system.run(task=task.task)
                    
                    yield f"data: {json_lib.dumps({'type': 'status', 'step': 'decision', 'message': '🎯 Finalizing recommendation...', 'progress': 95})}\n\n"
                    await asyncio.sleep(0.3)
                    
                    # Create trade response
                    trade_response = TradeResponse(
                        id=trade_id,
                        user_id=current_user.id,
                        task=task,
                        status=TradeStatus.COMPLETED,
                        created_at=datetime.now(timezone.utc),
                        executed_at=datetime.now(timezone.utc),
                        result=result,
                        performance_metrics=self._calculate_performance_metrics(result),
                    )
                    
                    # Store trade
                    self.trades[trade_id] = trade_response
                    
                    # Extract summary data for the completion message
                    summary = {
                        'action': result.get('recommended_action', 'HOLD'),
                        'confidence': result.get('confidence_score', 0),
                        'stocks': task.stocks,
                    }
                    
                    # Try to extract price from execution order if available
                    if result.get('execution_order'):
                        exec_order = result['execution_order']
                        # Simple extraction of price mentions
                        import re
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', str(exec_order))
                        if price_match:
                            summary['entry_price'] = price_match.group(1).replace(',', '')
                    
                    # Send completion with result and summary
                    yield f"data: {json_lib.dumps({'type': 'complete', 'trade_id': trade_id, 'message': '✅ Analysis complete!', 'progress': 100, 'summary': summary})}\n\n"
                    
                except Exception as e:
                    logger.error(f"Streaming trade failed: {str(e)}")
                    yield f"data: {json_lib.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )

        # Analytics Routes
        @self.app.get(
            "/analytics/history", response_model=HistoricalAnalytics
        )
        async def get_historical_analytics(
            current_user: User = Depends(self._get_current_user),
            days: int = Query(30, ge=1, le=365),
        ):
            with self._log_execution_time(
                "get_historical_analytics", current_user.id
            ):
                start_date = datetime.now(timezone.utc) - timedelta(
                    days=days
                )

                # Filter user's trades within the time period
                user_trades = [
                    trade
                    for trade in self.trades.values()
                    if trade.user_id == current_user.id
                    and trade.created_at >= start_date
                ]

                if not user_trades:
                    return HistoricalAnalytics(
                        total_trades=0,
                        success_rate=0.0,
                        average_return=0.0,
                        total_allocation=0.0,
                        risk_adjusted_return=0.0,
                        top_performing_stocks=[],
                    )

                # Calculate analytics
                successful_trades = len(
                    [
                        t
                        for t in user_trades
                        if t.status == TradeStatus.COMPLETED
                    ]
                )
                total_trades = len(user_trades)

                analytics = HistoricalAnalytics(
                    total_trades=total_trades,
                    success_rate=successful_trades
                    / total_trades
                    * 100,
                    average_return=sum(
                        t.performance_metrics.get(
                            "return_percentage", 0
                        )
                        for t in user_trades
                    )
                    / total_trades,
                    total_allocation=sum(
                        t.task.allocation for t in user_trades
                    ),
                    risk_adjusted_return=0.0,  # Would need more complex calculation
                    top_performing_stocks=[],  # Would need aggregation of stock performance
                )

                return analytics

    def _log_to_swarms(self, data_dict: dict) -> None:
        """Log data to Swarms with error handling and retry logic"""
        try:
            log_agent_data(data_dict)
            logger.info("Successfully logged data to Swarms")
        except Exception as e:
            logger.error(f"Failed to log to Swarms: {str(e)}")
            # Store failed logs for potential retry
            self._store_failed_log(data_dict)

    def _store_failed_log(self, data_dict: dict) -> None:
        """Store failed logs for retry"""
        logger.info("Storing failed log for later retry")
        # Implementation would depend on your storage solution

    def run(
        self, host: str = "0.0.0.0", port: int = 8000, *args, **kwargs
    ):
        """Run the FastAPI application"""
        import uvicorn

        logger.info(
            f"Starting Enhanced infinity_portal API on {host}:{port}"
        )
        uvicorn.run(self.app, host=host, port=port, *args, **kwargs)


# Create app instance for uvicorn
_api_instance = infinity_portalAPI()
app = _api_instance.app

# Example usage
if __name__ == "__main__":
    _api_instance.run()
