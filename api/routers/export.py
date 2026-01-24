"""
Export router - POST /export to generate markdown memos
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from models import ExportRequest, ExportResponse
from services.data_loader import (
    get_event_by_id,
    get_topics_for_event,
    get_posts_for_event,
    get_all_posts
)
from services.calculations import calculate_confidence

router = APIRouter(tags=["export"])


@router.post("/export", response_model=ExportResponse)
def export_event_memo(request: ExportRequest):
    """
    Export an event analysis as a markdown memo.

    The memo includes:
    - Event summary and price movement
    - Confidence assessment
    - Evidence-based narratives (topics)
    - Methodology and disclaimers
    """
    # Get event
    event = get_event_by_id(request.ticker, request.event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event {request.event_id} not found for ticker {request.ticker}"
        )

    # Get topics
    topics = get_topics_for_event(request.ticker, request.event_id)

    # Filter topics if specific ones selected
    if request.selected_topics:
        topics = [t for t in topics if t['id'] in request.selected_topics]

    # Get posts and calculate confidence
    posts = get_posts_for_event(request.ticker, request.event_id)
    all_posts = get_all_posts()
    confidence = calculate_confidence(event, topics, posts, all_posts)

    # Format dates
    window_start = event['window_start'][:10]  # Just date part
    window_end = event['window_end'][:10]

    # Generate markdown
    md = f"""# Stock Movement Analysis: {request.ticker} - {window_start} to {window_end}

**DISCLAIMER**: This memo presents evidence-based analysis of social media discussion patterns associated with stock price movements. It does NOT constitute investment advice, recommendations to buy/sell securities, or price targets. All analysis is based on static historical datasets and reflects correlation, not causation.

## Event Summary

- **Ticker**: {request.ticker}
- **Date Range**: {window_start} to {window_end}
- **Price Movement**: {event['move_pct']:+.1f}%
- **Volatility Score**: {event['vol_z']:.1f} standard deviations above baseline
- **Headline**: {event['headline']}

## Confidence Assessment

The following metrics assess the reliability of this analysis:

- **Coverage**: {confidence['coverage']:.1f}/100 (post volume vs baseline activity)
- **Sentiment Coherence**: {confidence['sentiment_coherence']:.1f}/100 (agreement across topics)
- **Recency**: {confidence['recency']:.1f}/100 (time decay from event date)
- **Overall Confidence**: {confidence['overall']:.1f}/100

## Evidence-Based Narratives

The following topics were identified in social media discussions during the event window. Evidence suggests these themes were associated with market attention during the price movement period.

"""

    # Add topics
    for i, topic in enumerate(topics, 1):
        md += f"\n### {i}. {topic['topic_label']}\n\n"
        md += f"- **Share of Discussion**: {topic['share_of_posts']*100:.1f}%\n"
        md += f"- **Sentiment Score**: {topic['sentiment_score']:+.2f} (scale: -1 to +1)\n"
        md += f"- **Keywords**: {', '.join(topic['keywords'])}\n"
        md += f"- **Supporting Evidence**: {len(topic['evidence_post_ids'])} posts\n"

        if request.include_counter_narratives and topic['counter_post_ids']:
            md += f"- **Counter-Narratives**: {len(topic['counter_post_ids'])} posts expressing contrasting views\n"

        md += "\n"

        # Add sample evidence citations
        if topic['evidence_post_ids']:
            md += f"*Sample evidence: Post IDs {', '.join(topic['evidence_post_ids'][:3])}*\n\n"

    # Add methodology section
    md += """
## Methodology & Data Sources

This analysis employs the following approach:

### Data Collection
- **Source**: Static social media dataset (Twitter/X platform)
- **Collection Method**: Historical archive, no live scraping
- **Time Window**: Posts published within the event date range
- **No External APIs**: All data processed from local dataset

### Analysis Techniques
- **Topic Clustering**: Pre-computed topic groups using NLP entity extraction
- **Sentiment Analysis**: Automated sentiment classification (positive/neutral/negative)
- **Volume Analysis**: Post counts compared to baseline activity
- **Coverage Metrics**: Share of discussion for each topic

### Important Limitations

**This is descriptive analysis only:**
- Social media discussion does NOT prove causation with price movements
- Correlation between discussion patterns and price changes does not imply one caused the other
- Sentiment analysis is automated and may contain classification errors
- Dataset limited to publicly available posts; does not reflect private information
- Analysis cannot account for institutional trading, insider information, or market microstructure
- This is educational/informational content for research purposes

**Not Investment Advice:**
- This memo does NOT constitute investment advice or recommendations
- No buy, sell, or hold recommendations are provided
- No price targets or forward-looking statements included
- Users must conduct independent analysis and consult qualified advisors

## Recordkeeping & Compliance

This memo is generated for recordkeeping and educational purposes to document evidence-based market narrative analysis. It should be used alongside traditional financial analysis, not as a replacement.

---

**Metadata**
- Dataset Version: 1.0 (static historical archive)
- Analysis Model: Correlation-based topic clustering
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- Platform: Trust-First Wealth Management Evidence Platform

*This document was generated using static datasets and automated analysis tools. Human review recommended before distribution to clients.*
"""

    # Create filename
    filename = f"{request.ticker}_{request.event_id}_analysis_{datetime.now().strftime('%Y%m%d')}.md"

    return ExportResponse(
        markdown=md,
        filename=filename
    )
