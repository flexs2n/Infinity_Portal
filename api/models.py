"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Instrument(BaseModel):
    """Stock instrument information"""
    ticker: str = Field(..., example="BA")
    name: str = Field(..., example="Boeing Co.")


class PricePoint(BaseModel):
    """Price and volume data point"""
    ticker: str
    ts: str  # ISO datetime string
    price: float
    volume: int


class Event(BaseModel):
    """Stock price movement event"""
    id: str
    ticker: str
    window_start: str  # ISO datetime string
    window_end: str  # ISO datetime string
    move_pct: float = Field(..., description="Percentage price change")
    vol_z: float = Field(..., description="Volume Z-score")
    headline: str


class EventTopicSummary(BaseModel):
    """Top topic for an event window"""
    event_id: str
    ticker: str
    window_start: str
    window_end: str
    topic_label: str
    share_of_posts: float = Field(..., ge=0, le=1)


class TopicTrendPoint(BaseModel):
    """Weekly time series point for topic impressions"""
    week_start: str  # ISO date string (YYYY-MM-DD)
    impressions: float


class TopicTrendSeries(BaseModel):
    """Weekly impressions for a topic label"""
    topic_label: str
    points: List[TopicTrendPoint]


class Topic(BaseModel):
    """Discussion topic within an event window"""
    id: str
    ticker: str
    window_start: str
    window_end: str
    topic_label: str
    keywords: List[str]
    share_of_posts: float = Field(..., ge=0, le=1)
    sentiment_score: float = Field(..., ge=-1, le=1)
    evidence_post_ids: List[str]
    counter_post_ids: List[str]


class Post(BaseModel):
    """Social media post"""
    id: str
    ts: str  # ISO datetime string
    platform: str = Field(..., example="twitter")
    author_handle: str
    text: str
    url_placeholder: str
    engagement: int = Field(..., description="Sum of likes + reposts + replies")


class ConfidenceMetrics(BaseModel):
    """Confidence assessment for an event"""
    coverage: float = Field(..., description="Post volume vs baseline (0-100)")
    sentiment_coherence: float = Field(..., description="Sentiment agreement (0-100)")
    recency: float = Field(..., description="Time decay from event (0-100)")
    overall: float = Field(..., description="Weighted overall confidence (0-100)")


class EventDetail(BaseModel):
    """Detailed event information with topics and posts"""
    event: Event
    topics: List[Topic]
    posts: List[Post]
    confidence: ConfidenceMetrics


class ExportRequest(BaseModel):
    """Request to export event analysis as markdown"""
    event_id: str
    ticker: str
    selected_topics: Optional[List[str]] = None
    include_counter_narratives: bool = True


class ExportResponse(BaseModel):
    """Exported markdown memo response"""
    markdown: str
    filename: str
