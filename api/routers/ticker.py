"""
Ticker router - price series, events, and event details
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import (
    PricePoint,
    Event,
    EventDetail,
    ConfidenceMetrics,
    EventTopicSummary,
    TopicTrendSeries,
    TopicTrendPoint
)
from services.data_loader import (
    get_price_series,
    get_events,
    get_event_by_id,
    get_topics_for_event,
    get_posts_for_event,
    get_all_posts
)
from services.calculations import calculate_confidence

router = APIRouter(tags=["ticker"])


@router.get("/ticker/{ticker}/series", response_model=List[PricePoint])
def get_ticker_series(
    ticker: str,
    start: Optional[str] = None,
    end: Optional[str] = None
):
    """
    Get price series for a ticker.

    Query params:
    - start: ISO datetime string to filter from (optional)
    - end: ISO datetime string to filter to (optional)
    """
    series = get_price_series(ticker, start, end)

    if not series:
        raise HTTPException(status_code=404, detail=f"No price data found for ticker {ticker}")

    return series


@router.get("/ticker/{ticker}/events", response_model=List[Event])
def get_ticker_events(ticker: str):
    """Get all events for a ticker"""
    events = get_events(ticker)

    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for ticker {ticker}")

    return events


@router.get("/ticker/{ticker}/event/{event_id}", response_model=EventDetail)
def get_event_detail(ticker: str, event_id: str):
    """
    Get detailed information for a specific event.

    Returns:
    - event: Event metadata
    - topics: List of discussion topics
    - posts: All referenced posts
    - confidence: Confidence metrics
    """
    # Get event
    event = get_event_by_id(ticker, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found for ticker {ticker}"
        )

    # Get topics
    topics = get_topics_for_event(ticker, event_id)

    # Get posts
    posts = get_posts_for_event(ticker, event_id)

    # Calculate confidence
    all_posts = get_all_posts()
    confidence = calculate_confidence(event, topics, posts, all_posts)

    return EventDetail(
        event=event,
        topics=topics,
        posts=posts,
        confidence=confidence
    )


@router.get("/ticker/{ticker}/topic-map", response_model=List[EventTopicSummary])
def get_ticker_topic_map(ticker: str):
    """Get the top topic per event window for timeline labeling."""
    events = get_events(ticker)
    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for ticker {ticker}")

    summaries: List[EventTopicSummary] = []
    for event in events:
        topics = get_topics_for_event(ticker, event["id"])
        if not topics:
            continue
        top_topic = max(topics, key=lambda t: t.get("share_of_posts", 0))
        summaries.append(EventTopicSummary(
            event_id=event["id"],
            ticker=event["ticker"],
            window_start=event["window_start"],
            window_end=event["window_end"],
            topic_label=top_topic["topic_label"],
            share_of_posts=top_topic.get("share_of_posts", 0)
        ))

    return summaries


@router.get("/ticker/{ticker}/topic-trends", response_model=List[TopicTrendSeries])
def get_ticker_topic_trends(ticker: str, top_n: int = 10):
    """Get weekly topic trends by engagement ("impressions")."""
    events = get_events(ticker)
    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for ticker {ticker}")

    topics = []
    for event in events:
        topics.extend(get_topics_for_event(ticker, event["id"]))

    if not topics:
        return []

    posts = get_all_posts()
    posts_by_id: Dict[str, Dict] = {p["id"]: p for p in posts}

    def week_start(ts: str) -> str:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        start = dt - timedelta(days=dt.weekday())
        return start.date().isoformat()

    # Aggregate impressions by topic label and week
    impressions_by_topic: Dict[str, Dict[str, float]] = {}
    total_by_topic: Dict[str, float] = {}
    all_weeks = set()

    for topic in topics:
        label = topic.get("topic_label", "Unknown")
        post_ids = set(topic.get("evidence_post_ids", [])) | set(topic.get("counter_post_ids", []))
        for post_id in post_ids:
            post = posts_by_id.get(post_id)
            if not post:
                continue
            week = week_start(post["ts"])
            all_weeks.add(week)
            impressions_by_topic.setdefault(label, {})
            impressions_by_topic[label][week] = impressions_by_topic[label].get(week, 0) + post.get("engagement", 0)
            total_by_topic[label] = total_by_topic.get(label, 0) + post.get("engagement", 0)

    if not impressions_by_topic:
        return []

    weeks_sorted = sorted(all_weeks)
    top_topics = sorted(total_by_topic.items(), key=lambda item: item[1], reverse=True)[:top_n]

    series: List[TopicTrendSeries] = []
    for label, _ in top_topics:
        points = [
            TopicTrendPoint(
                week_start=week,
                impressions=round(impressions_by_topic.get(label, {}).get(week, 0), 2)
            )
            for week in weeks_sorted
        ]
        series.append(TopicTrendSeries(topic_label=label, points=points))

    return series
