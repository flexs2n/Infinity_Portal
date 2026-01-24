"""
Transform Boeing_clean.csv into sample.json for the wealth management app.
Creates events, topics, and posts from the Boeing Twitter dataset.
"""

import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import random

# Boeing events from 2019 with known price impacts
BA_EVENTS = [
    {
        'id': 'ba_737max_grounding',
        'window_start': '2019-03-10',
        'window_end': '2019-03-16',
        'move_pct': -11.2,
        'headline': 'Discussion patterns associated with 737 MAX fleet grounding'
    },
    {
        'id': 'ba_ceo_resignation',
        'window_start': '2019-12-20',
        'window_end': '2019-12-26',
        'move_pct': -4.3,
        'headline': 'Social media response to executive leadership transition'
    },
    {
        'id': 'ba_production_halt',
        'window_start': '2019-12-13',
        'window_end': '2019-12-19',
        'move_pct': -3.8,
        'headline': '737 MAX production suspension announcement coverage'
    }
]

# Apple events (synthetic)
AAPL_EVENTS = [
    {
        'id': 'aapl_iphone11_launch',
        'window_start': '2019-09-10',
        'window_end': '2019-09-16',
        'move_pct': 5.8,
        'headline': 'Market response to iPhone 11 product announcement'
    },
    {
        'id': 'aapl_trade_concerns',
        'window_start': '2019-05-05',
        'window_end': '2019-05-11',
        'move_pct': -6.4,
        'headline': 'Discussion of trade policy impact on supply chain'
    },
    {
        'id': 'aapl_services_growth',
        'window_start': '2019-01-29',
        'window_end': '2019-02-04',
        'move_pct': 7.2,
        'headline': 'Investor attention to services segment expansion'
    }
]


def cluster_to_topic_label(cluster_str):
    """Convert cluster keywords to human-readable topic label"""
    if not cluster_str:
        return "General Discussion"

    mapping = {
        'ceo, boeing ceo, calhoun, muilenburg': 'CEO Leadership Changes',
        '737 max, max, faa, pilot': '737 MAX Regulatory Issues',
        'suspend, production, resume, max production': 'Production & Manufacturing',
        'loss, boeing shares, share, fall': 'Stock Performance Concerns',
        'starliner, space, astronaut, launch': 'Space Program Developments',
        'coronavirus, $ba, business, company': 'Broader Market Factors',
        'crash, ethiopian airlines, lion air, victim': 'Safety Incident Coverage',
        'plane, aircraft, flight, airline': 'Aircraft Operations',
        'deliveries, orders, customer, cancel': 'Order Book & Deliveries',
        'trump, administration, government, pentagon': 'Government Relations',
    }

    # Try exact match first
    if cluster_str in mapping:
        return mapping[cluster_str]

    # Otherwise title-case the first keyword
    keywords = cluster_str.split(', ')
    if keywords:
        return keywords[0].title() + " Related"

    return "General Discussion"


def calculate_vol_z(posts_count, avg_posts_per_day):
    """Calculate volatility Z-score from post volume"""
    if avg_posts_per_day == 0:
        return 0.0
    # Assume std dev is ~30% of average
    std_dev = avg_posts_per_day * 0.3
    if std_dev == 0:
        return 0.0
    return (posts_count - avg_posts_per_day) / std_dev


def parse_date(date_str):
    """Parse date string to datetime"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None


def transform_post(row, post_id):
    """Transform CSV row to post object"""
    # Parse engagement metrics
    likes = int(row.get('X Likes', 0) or 0)
    reposts = int(row.get('X Reposts', 0) or 0)
    replies = int(row.get('X Replies', 0) or 0)
    engagement = likes + reposts + replies

    return {
        'id': post_id,
        'ts': row['Date'],
        'platform': 'twitter',
        'author_handle': row.get('Author', 'unknown').strip(),
        'text': row.get('Snippet', row.get('Title', ''))[:500],  # Limit length
        'url_placeholder': row.get('Original Url', ''),
        'engagement': engagement
    }


def extract_topics_for_event(event, posts_in_window, ticker):
    """Extract topics from posts within event window"""
    cluster_posts = defaultdict(list)

    # Group posts by cluster
    for post in posts_in_window:
        cluster = post.get('cluster', '').strip()
        if cluster:
            cluster_posts[cluster].append(post)

    topics = []
    total_posts = len(posts_in_window)

    if total_posts == 0:
        return []

    for cluster, cluster_post_list in cluster_posts.items():
        # Calculate sentiment
        sentiments = []
        for p in cluster_post_list:
            sent = p.get('sentiment', 'neutral').lower()
            if sent == 'positive':
                sentiments.append(1)
            elif sent == 'negative':
                sentiments.append(-1)
            else:
                sentiments.append(0)

        avg_sentiment = statistics.mean(sentiments) if sentiments else 0

        # Split into evidence vs counter based on sentiment
        evidence_ids = []
        counter_ids = []

        for p in cluster_post_list:
            sent = p.get('sentiment', 'neutral').lower()
            post_id = p['post_id']

            if sent in ['positive', 'neutral']:
                evidence_ids.append(post_id)
            else:
                counter_ids.append(post_id)

        # Create topic object
        keywords = cluster.split(', ')[:5]
        topic = {
            'id': f"{event['id']}_{cluster[:20].replace(' ', '_').replace(',', '')}",
            'ticker': ticker,
            'window_start': event['window_start'],
            'window_end': event['window_end'],
            'topic_label': cluster_to_topic_label(cluster),
            'keywords': keywords,
            'share_of_posts': round(len(cluster_post_list) / total_posts, 3),
            'sentiment_score': round(avg_sentiment, 2),
            'evidence_post_ids': evidence_ids[:15],
            'counter_post_ids': counter_ids[:10]
        }
        topics.append(topic)

    # Sort by share_of_posts descending, take top 8
    topics.sort(key=lambda t: t['share_of_posts'], reverse=True)
    return topics[:8]


def generate_price_series(ticker, events, start_date='2019-01-01', end_date='2019-12-31'):
    """Generate synthetic but realistic price data"""
    from datetime import date as dt_date

    # Parse dates
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Base prices
    if ticker == 'BA':
        base_price = 350.0
        trend_per_day = -0.08  # Slight downtrend
        base_volume = 4000000
    else:  # AAPL
        base_price = 175.0
        trend_per_day = 0.15  # Slight uptrend
        base_volume = 25000000

    prices = []
    current_date = start
    day_index = 0

    while current_date <= end:
        # Skip weekends
        if current_date.weekday() < 5:
            # Calculate base price with trend
            price = base_price + (trend_per_day * day_index)

            # Check if this date falls in any event window
            event_impact = 1.0
            for event in events:
                ev_start = datetime.strptime(event['window_start'], '%Y-%m-%d').date()
                ev_end = datetime.strptime(event['window_end'], '%Y-%m-%d').date()

                if ev_start <= current_date <= ev_end:
                    # Apply event impact gradually over window
                    days_in_window = (ev_end - ev_start).days + 1
                    impact_per_day = event['move_pct'] / 100 / days_in_window
                    event_impact += impact_per_day

            price *= event_impact

            # Add random noise (±1%)
            noise = random.uniform(-0.01, 0.01)
            price *= (1 + noise)

            # Generate volume with random variation
            volume = int(base_volume * random.uniform(0.8, 1.5))

            prices.append({
                'ticker': ticker,
                'ts': current_date.isoformat() + 'T16:00:00Z',
                'price': round(price, 2),
                'volume': volume
            })

            day_index += 1

        current_date += timedelta(days=1)

    return prices


def main():
    print("Loading Boeing_clean.csv...")

    # Load CSV data
    posts_by_date = defaultdict(list)
    all_posts = []

    with open('../Boeing_clean.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            date_str = row.get('Date', '')
            if not date_str:
                continue

            # Extract just the date part (YYYY-MM-DD)
            date_key = date_str[:10]

            post_data = {
                'row': row,
                'cluster': row.get('gx_cluster', '').strip(),
                'sentiment': row.get('Sentiment', 'neutral'),
                'post_id': f"ba_{idx}",
                'date': date_str
            }

            posts_by_date[date_key].append(post_data)
            all_posts.append(post_data)

    print(f"Loaded {len(all_posts)} posts")

    # Calculate baseline posts per day
    if posts_by_date:
        avg_posts_per_day = len(all_posts) / len(posts_by_date)
    else:
        avg_posts_per_day = 1

    print(f"Average posts per day: {avg_posts_per_day:.1f}")

    # Build output structure
    output = {
        'instruments': [
            {'ticker': 'BA', 'name': 'Boeing Co.'},
            {'ticker': 'AAPL', 'name': 'Apple Inc.'}
        ],
        'price_series': [],
        'events': [],
        'topics': [],
        'posts': []
    }

    # Process Boeing events
    print("\nProcessing Boeing events...")
    for event in BA_EVENTS:
        print(f"  Processing: {event['headline'][:50]}...")

        # Get posts in window
        posts_in_window = []
        start_date = datetime.strptime(event['window_start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(event['window_end'], '%Y-%m-%d').date()

        current = start_date
        while current <= end_date:
            date_key = current.isoformat()
            posts_in_window.extend(posts_by_date.get(date_key, []))
            current += timedelta(days=1)

        print(f"    Found {len(posts_in_window)} posts in window")

        # Calculate vol_z
        vol_z = calculate_vol_z(len(posts_in_window), avg_posts_per_day)

        # Add event
        output['events'].append({
            'id': event['id'],
            'ticker': 'BA',
            'window_start': event['window_start'] + 'T00:00:00Z',
            'window_end': event['window_end'] + 'T23:59:59Z',
            'move_pct': event['move_pct'],
            'vol_z': round(vol_z, 2),
            'headline': event['headline']
        })

        # Extract topics
        topics = extract_topics_for_event(event, posts_in_window, 'BA')
        print(f"    Extracted {len(topics)} topics")
        output['topics'].extend(topics)

        # Add sample posts (limit to avoid huge file)
        sample_posts = random.sample(posts_in_window, min(50, len(posts_in_window)))
        for post_data in sample_posts:
            output['posts'].append(transform_post(post_data['row'], post_data['post_id']))

    # Generate synthetic AAPL data
    print("\nGenerating synthetic AAPL data...")
    aapl_post_id = 0

    for event in AAPL_EVENTS:
        print(f"  Creating: {event['headline'][:50]}...")

        # Add event
        output['events'].append({
            'id': event['id'],
            'ticker': 'AAPL',
            'window_start': event['window_start'] + 'T00:00:00Z',
            'window_end': event['window_end'] + 'T23:59:59Z',
            'move_pct': event['move_pct'],
            'vol_z': round(random.uniform(1.5, 3.5), 2),
            'headline': event['headline']
        })

        # Create synthetic topics for AAPL
        aapl_topics = [
            {
                'id': f"{event['id']}_product_features",
                'ticker': 'AAPL',
                'window_start': event['window_start'] + 'T00:00:00Z',
                'window_end': event['window_end'] + 'T23:59:59Z',
                'topic_label': 'Product Features & Innovation',
                'keywords': ['iphone', 'camera', 'features', 'specs'],
                'share_of_posts': 0.35,
                'sentiment_score': 0.65,
                'evidence_post_ids': [f"aapl_{aapl_post_id + i}" for i in range(12)],
                'counter_post_ids': [f"aapl_{aapl_post_id + 20 + i}" for i in range(3)]
            },
            {
                'id': f"{event['id']}_pricing",
                'ticker': 'AAPL',
                'window_start': event['window_start'] + 'T00:00:00Z',
                'window_end': event['window_end'] + 'T23:59:59Z',
                'topic_label': 'Pricing & Market Position',
                'keywords': ['price', 'expensive', 'value', 'competition'],
                'share_of_posts': 0.25,
                'sentiment_score': -0.15,
                'evidence_post_ids': [f"aapl_{aapl_post_id + 30 + i}" for i in range(8)],
                'counter_post_ids': [f"aapl_{aapl_post_id + 40 + i}" for i in range(5)]
            },
            {
                'id': f"{event['id']}_services",
                'ticker': 'AAPL',
                'window_start': event['window_start'] + 'T00:00:00Z',
                'window_end': event['window_end'] + 'T23:59:59Z',
                'topic_label': 'Services Revenue Growth',
                'keywords': ['services', 'subscription', 'revenue', 'growth'],
                'share_of_posts': 0.20,
                'sentiment_score': 0.75,
                'evidence_post_ids': [f"aapl_{aapl_post_id + 50 + i}" for i in range(10)],
                'counter_post_ids': [f"aapl_{aapl_post_id + 60 + i}" for i in range(2)]
            },
        ]

        output['topics'].extend(aapl_topics)

        # Create synthetic posts for AAPL
        for i in range(40):
            output['posts'].append({
                'id': f"aapl_{aapl_post_id}",
                'ts': event['window_start'] + f'T{random.randint(9, 21):02d}:{random.randint(0, 59):02d}:00Z',
                'platform': 'twitter',
                'author_handle': f"tech_analyst_{random.randint(1, 999)}",
                'text': f"Sample AAPL discussion post about {event['headline'].lower()}. Evidence suggests market attention to key developments.",
                'url_placeholder': f"https://twitter.com/example/{aapl_post_id}",
                'engagement': random.randint(10, 5000)
            })
            aapl_post_id += 1

    # Generate price series for both tickers
    print("\nGenerating price series...")
    output['price_series'].extend(generate_price_series('BA', BA_EVENTS))
    output['price_series'].extend(generate_price_series('AAPL', AAPL_EVENTS))

    # Write output
    print("\nWriting sample.json...")
    with open('sample.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Generated sample.json with:")
    print(f"  - {len(output['instruments'])} instruments")
    print(f"  - {len(output['events'])} events")
    print(f"  - {len(output['topics'])} topics")
    print(f"  - {len(output['posts'])} posts")
    print(f"  - {len(output['price_series'])} price points")


if __name__ == '__main__':
    main()
