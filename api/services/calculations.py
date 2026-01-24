"""
Confidence calculations and other metrics
"""

import statistics
from datetime import datetime
from typing import List, Dict


def calculate_confidence(event: Dict, topics: List[Dict], posts: List[Dict], all_posts: List[Dict]) -> Dict:
    """
    Calculate confidence metrics for an event.

    Returns dict with:
    - coverage: Post volume vs baseline (0-100)
    - sentiment_coherence: Sentiment agreement across topics (0-100)
    - recency: Time decay from event date (0-100)
    - overall: Weighted average (0-100)
    """

    # 1. COVERAGE: posts in window vs baseline
    window_start = datetime.fromisoformat(event['window_start'].replace('Z', '+00:00'))
    window_end = datetime.fromisoformat(event['window_end'].replace('Z', '+00:00'))
    window_days = (window_end - window_start).days + 1

    posts_in_window = len(posts)

    # Calculate baseline (avg posts per day across dataset)
    # Assume dataset spans ~365 days
    if all_posts:
        baseline_posts_per_day = len(all_posts) / 365
        expected_posts = baseline_posts_per_day * window_days
        coverage = min(100.0, (posts_in_window / expected_posts) * 100) if expected_posts > 0 else 50.0
    else:
        coverage = 50.0

    # 2. SENTIMENT COHERENCE: 1 - std_dev of sentiment scores
    # Only consider topics with significant share (>5%)
    significant_topics = [t for t in topics if t['share_of_posts'] > 0.05]
    sentiment_scores = [t['sentiment_score'] for t in significant_topics]

    if len(sentiment_scores) > 1:
        std_dev = statistics.stdev(sentiment_scores)
        # Normalize std_dev (range 0-2 for sentiment -1 to +1)
        # Lower std_dev = higher coherence
        coherence = max(0.0, (1 - (std_dev / 2)) * 100)
    elif len(sentiment_scores) == 1:
        coherence = 75.0  # Single strong topic is reasonably coherent
    else:
        coherence = 50.0  # No significant topics = neutral

    # 3. RECENCY: exponential decay from event end date
    now = datetime.now(window_end.tzinfo)
    days_since_event = (now - window_end).days

    # Decay factor: 0.95^days (95% per day)
    if days_since_event >= 0:
        recency = max(0.0, 100.0 * (0.95 ** days_since_event))
    else:
        # Future event (shouldn't happen, but handle gracefully)
        recency = 100.0

    # 4. OVERALL: weighted average
    # Coverage is most important (40%), then coherence (30%), then recency (30%)
    overall = (coverage * 0.4) + (coherence * 0.3) + (recency * 0.3)

    return {
        'coverage': round(coverage, 1),
        'sentiment_coherence': round(coherence, 1),
        'recency': round(recency, 1),
        'overall': round(overall, 1)
    }


def calculate_engagement_weighted_share(topics: List[Dict], posts: List[Dict]) -> List[Dict]:
    """
    Recalculate topic share_of_posts weighted by engagement instead of count.

    Returns topics with updated share_of_posts based on engagement.
    """
    # Build post_id -> engagement map
    post_engagement = {p['id']: p['engagement'] for p in posts}

    # Calculate engagement for each topic
    topic_engagement = []
    total_engagement = 0

    for topic in topics:
        # Sum engagement for all evidence + counter posts
        all_post_ids = topic['evidence_post_ids'] + topic['counter_post_ids']
        engagement = sum(post_engagement.get(pid, 0) for pid in all_post_ids)

        topic_engagement.append({
            'topic': topic,
            'engagement': engagement
        })
        total_engagement += engagement

    # Update share_of_posts
    updated_topics = []
    for item in topic_engagement:
        topic = item['topic'].copy()
        if total_engagement > 0:
            topic['share_of_posts'] = round(item['engagement'] / total_engagement, 3)
        updated_topics.append(topic)

    # Re-sort by new share
    updated_topics.sort(key=lambda t: t['share_of_posts'], reverse=True)

    return updated_topics
