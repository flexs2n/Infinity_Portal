"""
Data loader service - loads and caches sample.json data
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

# Global cache for loaded data
_data_cache: Optional[Dict] = None


def load_data() -> Dict:
    """Load sample.json into memory (cached)"""
    global _data_cache

    if _data_cache is not None:
        return _data_cache

    # Load from file
    data_path = Path(__file__).parent.parent.parent / "data" / "sample.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        _data_cache = json.load(f)

    print(f"✓ Loaded data: {len(_data_cache.get('posts', []))} posts, {len(_data_cache.get('events', []))} events")

    return _data_cache


def get_instruments() -> List[Dict]:
    """Get all instruments"""
    data = load_data()
    return data.get('instruments', [])


def get_price_series(ticker: str, start: Optional[str] = None, end: Optional[str] = None) -> List[Dict]:
    """Get price series for a ticker, optionally filtered by date range"""
    data = load_data()
    series = [p for p in data.get('price_series', []) if p['ticker'] == ticker]

    # Filter by date range if provided
    if start:
        series = [p for p in series if p['ts'] >= start]
    if end:
        series = [p for p in series if p['ts'] <= end]

    # Sort by timestamp
    series.sort(key=lambda p: p['ts'])

    return series


def get_events(ticker: str) -> List[Dict]:
    """Get all events for a ticker"""
    data = load_data()
    events = [e for e in data.get('events', []) if e['ticker'] == ticker]

    # Sort by window_start descending
    events.sort(key=lambda e: e['window_start'], reverse=True)

    return events


def get_event_by_id(ticker: str, event_id: str) -> Optional[Dict]:
    """Get a specific event by ID"""
    data = load_data()
    events = [e for e in data.get('events', []) if e['ticker'] == ticker and e['id'] == event_id]

    return events[0] if events else None


def get_topics_for_event(ticker: str, event_id: str) -> List[Dict]:
    """Get all topics for an event"""
    data = load_data()

    # Find the event first to get window dates
    event = get_event_by_id(ticker, event_id)
    if not event:
        return []

    # Find topics matching this event
    topics = [
        t for t in data.get('topics', [])
        if t['ticker'] == ticker and t['id'].startswith(event_id)
    ]

    # Sort by share_of_posts descending
    topics.sort(key=lambda t: t['share_of_posts'], reverse=True)

    return topics


def get_posts_for_event(ticker: str, event_id: str) -> List[Dict]:
    """Get all posts referenced in an event's topics"""
    data = load_data()
    topics = get_topics_for_event(ticker, event_id)

    # Collect all post IDs from topics
    post_ids = set()
    for topic in topics:
        post_ids.update(topic.get('evidence_post_ids', []))
        post_ids.update(topic.get('counter_post_ids', []))

    # Get the actual posts
    all_posts = data.get('posts', [])
    posts = [p for p in all_posts if p['id'] in post_ids]

    # Sort by timestamp descending
    posts.sort(key=lambda p: p['ts'], reverse=True)

    return posts


def get_all_posts() -> List[Dict]:
    """Get all posts (for baseline calculations)"""
    data = load_data()
    return data.get('posts', [])
