#!/usr/bin/env python3
"""
Initialize the SQLite database from Boeing CSV data
"""
import sqlite3
import pandas as pd
import os

CSV_PATH = '/Users/kazybekkhairulla/Developer/Infinity_Portal/dataf/Boeing_clean_clustered_full.csv'
DB_PATH = '/Users/kazybekkhairulla/Developer/Infinity_Portal/dataf/tweets_full.db'

def init_database():
    """Create and populate the tweets database"""
    print(f"Reading CSV from: {CSV_PATH}")
    
    # Read CSV
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Rename columns to match what the API expects
    column_mapping = {
        'Date': 'date',
        'Title': 'title',
        'Snippet': 'snippet',
        'Author': 'author',
        'Impressions': 'impressions',
        'Reach (new)': 'reach',
        'Potential Audience': 'potential_audience',
        'Country': 'country',
        'Region': 'region',
        'City': 'city',
        'Account Type': 'account_type',
        'X Followers': 'x_followers',
        'X Likes': 'x_likes',
        'X Reposts': 'x_reposts',
        'Sentiment': 'sentiment',
        'Emotion': 'emotion',
        'gx_cardiff_nlp_sentiment': 'gx_sentiment',
        'gx_joeddav_emotion': 'gx_emotion',
        'gx_cluster': 'cluster',
        'Hashtags': 'hashtags',
        'Engagement Score': 'engagement_score',
        'Impact': 'impact',
    }
    
    # Rename columns that exist
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Select only the columns we need
    needed_columns = list(column_mapping.values())
    available_columns = [col for col in needed_columns if col in df.columns]
    df = df[available_columns]
    
    print(f"Selected columns: {available_columns}")
    
    # Remove old database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database")
    
    # Create SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    # Write to database
    df.to_sql('tweets', conn, index=False, if_exists='replace')
    print(f"Wrote {len(df)} rows to database")
    
    # Create indexes for better query performance
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cluster ON tweets(cluster)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON tweets(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON tweets(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gx_sentiment ON tweets(gx_sentiment)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_impressions ON tweets(impressions)')
    conn.commit()
    print("Created indexes")
    
    # Verify
    count = cursor.execute('SELECT COUNT(*) FROM tweets').fetchone()[0]
    print(f"Database created successfully with {count} tweets")
    
    # Show sample
    sample = cursor.execute('SELECT cluster, COUNT(*) as cnt FROM tweets GROUP BY cluster LIMIT 5').fetchall()
    print(f"Sample clusters: {sample}")
    
    conn.close()
    print(f"Database saved to: {DB_PATH}")

if __name__ == '__main__':
    init_database()
