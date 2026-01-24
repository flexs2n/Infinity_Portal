"""
Edge Discovery API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime

# Adjust import path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infinity_portal.autonomous_strategy_system import AutonomousStrategySystem

router = APIRouter(prefix="/edges", tags=["Edge Discovery"])


class EdgeDiscoveryRequest(BaseModel):
    """Request model for edge discovery"""
    ticker: str = Field(..., description="Stock ticker symbol", example="NVDA")
    days_back: int = Field(7, description="Days of historical data", ge=1, le=30)
    include_social: bool = Field(True, description="Include social media analysis")
    include_news: bool = Field(True, description="Include news analysis")


class EdgeResponse(BaseModel):
    """Response model for a single edge"""
    edge_id: str
    edge_name: str
    edge_type: str
    description: str
    confidence: float = Field(..., ge=0, le=1)
    expected_sharpe: float
    expected_win_rate: float = Field(..., ge=0, le=1)
    entry_conditions: List[str]
    exit_conditions: List[str]
    risk_factors: List[str]


class EdgeDiscoveryResponse(BaseModel):
    """Response model for edge discovery"""
    ticker: str
    edges_found: int
    edges: List[EdgeResponse]
    data_quality: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data_sources_used: Dict[str, bool]


@router.post("/discover", response_model=EdgeDiscoveryResponse)
async def discover_edges(
    request: EdgeDiscoveryRequest,
    background_tasks: BackgroundTasks
):
    """
    Discover trading edges for a given ticker
    
    This endpoint:
    1. Collects social media data (if enabled)
    2. Collects news data (if enabled)
    3. Analyzes price data
    4. Uses AI to identify trading edges
    
    Returns a list of discovered edges with confidence scores
    """
    try:
        logger.info(f"🔍 Starting edge discovery for {request.ticker}")
        
        # Initialize system
        system = AutonomousStrategySystem()
        
        # Collect data
        logger.info("📡 Collecting data...")
        data = system.collect_data(request.ticker)
        
        # Find edges
        logger.info("🧠 Analyzing for edges...")
        edges_result = system.discover_edges(request.ticker, data)
        
        # Format response
        edges_list = []
        for edge in edges_result.get('edges_discovered', []):
            edges_list.append(EdgeResponse(**edge))
        
        response = EdgeDiscoveryResponse(
            ticker=request.ticker,
            edges_found=len(edges_list),
            edges=edges_list,
            data_quality=edges_result.get('data_quality', 'unknown'),
            data_sources_used={
                'social_media': request.include_social,
                'news': request.include_news,
                'price_data': True
            }
        )
        
        logger.info(f"✅ Discovered {len(edges_list)} edges for {request.ticker}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Edge discovery failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Edge discovery failed: {str(e)}"
        )


@router.get("/{ticker}/historical", response_model=List[EdgeResponse])
async def get_historical_edges(
    ticker: str,
    limit: int = 10
):
    """
    Get previously discovered edges for a ticker
    
    NOTE: This requires database integration
    Currently returns empty list as placeholder
    """
    logger.info(f"📚 Fetching historical edges for {ticker}")
    
    # TODO: Implement database query
    # This would query a database of previously discovered edges
    
    return []


@router.get("/types", response_model=List[str])
async def get_edge_types():
    """
    Get list of supported edge types
    """
    return [
        "sentiment_momentum",
        "news_divergence",
        "social_volume_spike",
        "institutional_flow",
        "technical_breakout",
        "earnings_surprise",
        "contrarian_signal"
    ]


@router.post("/{edge_id}/validate")
async def validate_edge(edge_id: str, ticker: str):
    """
    Validate an edge against recent data
    
    This re-checks if an edge is still valid
    """
    logger.info(f"✅ Validating edge {edge_id} for {ticker}")
    
    # TODO: Implement edge validation logic
    
    return {
        "edge_id": edge_id,
        "ticker": ticker,
        "is_valid": True,
        "confidence": 0.75,
        "message": "Edge validation coming soon"
    }