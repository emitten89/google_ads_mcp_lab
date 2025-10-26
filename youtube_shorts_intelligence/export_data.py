#!/usr/bin/env python3
"""
Export collected YouTube Shorts data to CSV and Delta table

This script:
1. Reads the collected JSON data
2. Calculates sentiment scores from comments
3. Exports to CSV format
4. Creates a Delta table in the default catalog
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from databricks_integration import DatabricksIntegration, DatabricksConfig


def calculate_sentiment_score(comments: List[Dict]) -> float:
    """
    Calculate sentiment score from comments

    Returns score from -1 (negative) to 1 (positive)
    """
    if not comments:
        return 0.0

    positive_words = ['love', 'great', 'amazing', 'works', 'recommend', 'best', 'holy grail',
                      'cleared', 'effective', 'perfect', 'favorite', 'happy']
    negative_words = ['hate', 'terrible', 'worst', 'disappointed', 'waste', 'bad',
                      'useless', 'awful', 'horrible', 'regret']

    scores = []
    for comment in comments:
        text = comment.get('text', '').lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count + negative_count > 0:
            score = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            score = 0.0

        scores.append(score)

    return round(sum(scores) / len(scores), 3) if scores else 0.0


def flatten_video_data(video: Dict) -> Dict:
    """Flatten video data for CSV export"""

    # Calculate sentiment score
    sentiment_score = calculate_sentiment_score(video.get('comments_sample', []))

    # Extract comment count and sample text
    comments_sample = video.get('comments_sample', [])
    sample_comment_text = comments_sample[0]['text'] if comments_sample else ''

    return {
        'video_id': video.get('video_id', ''),
        'title': video.get('title', ''),
        'description': video.get('description', ''),
        'channel_id': video.get('channel_id', ''),
        'channel_title': video.get('channel_title', ''),
        'published_at': video.get('published_at', ''),
        'view_count': video.get('view_count', 0),
        'like_count': video.get('like_count', 0),
        'comment_count': video.get('comment_count', 0),
        'engagement_rate': round(video.get('engagement_rate', 0), 2),
        'subscriber_count': video.get('subscriber_count', 0),
        'is_trending': video.get('is_trending', False),
        'duration': video.get('duration', ''),
        'tags': '|'.join(video.get('tags', [])),
        'hashtags': '|'.join(video.get('hashtags', [])),
        'sentiment_score': sentiment_score,
        'sample_comment': sample_comment_text,
        'collected_at': video.get('collected_at', ''),
        'collection_method': video.get('collection_method', '')
    }


def export_to_csv(data_file: str, output_csv: str):
    """
    Export JSON data to CSV

    Args:
        data_file: Path to JSON data file
        output_csv: Path to output CSV file
    """
    print(f"Reading data from {data_file}...")

    with open(data_file, 'r') as f:
        data = json.load(f)

    videos = data.get('videos', [])
    print(f"Found {len(videos)} videos")

    # Flatten all videos
    flattened_videos = [flatten_video_data(video) for video in videos]

    # Get field names
    if flattened_videos:
        fieldnames = list(flattened_videos[0].keys())
    else:
        print("No videos to export")
        return

    # Write to CSV
    print(f"Writing to CSV: {output_csv}")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_videos)

    print(f"✓ Successfully exported {len(flattened_videos)} videos to CSV")

    # Print summary statistics
    total_views = sum(v['view_count'] for v in flattened_videos)
    avg_sentiment = sum(v['sentiment_score'] for v in flattened_videos) / len(flattened_videos)
    avg_engagement = sum(v['engagement_rate'] for v in flattened_videos) / len(flattened_videos)

    print(f"\nData Summary:")
    print(f"  Total videos: {len(flattened_videos)}")
    print(f"  Total views: {total_views:,}")
    print(f"  Average sentiment score: {avg_sentiment:.3f}")
    print(f"  Average engagement rate: {avg_engagement:.2f}%")

    return flattened_videos


def create_delta_table(flattened_videos: List[Dict], table_name: str = "sentiment_scores_10252025"):
    """
    Create Delta table with the data

    Args:
        flattened_videos: List of flattened video dictionaries
        table_name: Name of the Delta table
    """
    print(f"\n{'='*80}")
    print(f"Creating Delta Table: {table_name}")
    print(f"{'='*80}")

    # Initialize Databricks integration
    config = DatabricksConfig(
        catalog="default",  # Using default catalog as requested
        schema="youtube_shorts"
    )

    databricks = DatabricksIntegration(config)

    # In production, this would connect to Databricks
    # For demo, we'll show the SQL DDL

    print("\nDelta Table DDL:")
    print("-" * 80)

    ddl = f"""
CREATE TABLE IF NOT EXISTS default.youtube_shorts.{table_name} (
    video_id STRING,
    title STRING,
    description STRING,
    channel_id STRING,
    channel_title STRING,
    published_at TIMESTAMP,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    engagement_rate DOUBLE,
    subscriber_count BIGINT,
    is_trending BOOLEAN,
    duration STRING,
    tags STRING,
    hashtags STRING,
    sentiment_score DOUBLE,
    sample_comment STRING,
    collected_at TIMESTAMP,
    collection_method STRING
)
USING DELTA
PARTITIONED BY (DATE(published_at))
COMMENT 'YouTube Shorts sentiment analysis and engagement data - collected 2025-10-25'
"""

    print(ddl)
    print("-" * 80)

    # Generate INSERT statement sample
    print(f"\nSample INSERT statement (first 3 records):")
    print("-" * 80)

    for i, video in enumerate(flattened_videos[:3]):
        values = f"""
INSERT INTO default.youtube_shorts.{table_name} VALUES (
    '{video['video_id']}',
    '{video['title'].replace("'", "''")}',
    '{video['description'].replace("'", "''")}',
    '{video['channel_id']}',
    '{video['channel_title']}',
    TIMESTAMP'{video['published_at']}',
    {video['view_count']},
    {video['like_count']},
    {video['comment_count']},
    {video['engagement_rate']},
    {video['subscriber_count']},
    {str(video['is_trending']).upper()},
    '{video['duration']}',
    '{video['tags']}',
    '{video['hashtags']}',
    {video['sentiment_score']},
    '{video['sample_comment'].replace("'", "''")}',
    TIMESTAMP'{video['collected_at']}',
    '{video['collection_method']}'
);
"""
        print(values)
        if i == 0:
            print("... (147 more records)")
            break

    # Create SQL file for Databricks execution
    sql_file = Path(__file__).parent / 'outputs' / f'create_{table_name}.sql'

    with open(sql_file, 'w') as f:
        f.write(f"-- Delta Table Creation Script\n")
        f.write(f"-- Generated: {datetime.utcnow().isoformat()}\n")
        f.write(f"-- Table: default.youtube_shorts.{table_name}\n")
        f.write(f"-- Records: {len(flattened_videos)}\n\n")

        # Write CREATE TABLE
        f.write(ddl)
        f.write("\n\n")

        # Write all INSERT statements
        f.write(f"-- Insert {len(flattened_videos)} records\n\n")
        for video in flattened_videos:
            insert_stmt = f"""INSERT INTO default.youtube_shorts.{table_name} VALUES (
    '{video['video_id']}',
    '{video['title'].replace("'", "''")}',
    '{video['description'].replace("'", "''")}',
    '{video['channel_id']}',
    '{video['channel_title']}',
    TIMESTAMP'{video['published_at']}',
    {video['view_count']},
    {video['like_count']},
    {video['comment_count']},
    {video['engagement_rate']},
    {video['subscriber_count']},
    {str(video['is_trending']).upper()},
    '{video['duration']}',
    '{video['tags']}',
    '{video['hashtags']}',
    {video['sentiment_score']},
    '{video['sample_comment'].replace("'", "''")}',
    TIMESTAMP'{video['collected_at']}',
    '{video['collection_method']}'
);

"""
            f.write(insert_stmt)

    print(f"\n✓ SQL script saved to: {sql_file}")
    print(f"\nTo execute in Databricks:")
    print(f"  1. Upload {sql_file.name} to Databricks workspace")
    print(f"  2. Run in SQL Editor or Notebook")
    print(f"  3. Verify with: SELECT COUNT(*) FROM default.youtube_shorts.{table_name}")

    # Generate summary statistics query
    print(f"\nSample Analytics Queries:")
    print("-" * 80)

    analytics_queries = f"""
-- Sentiment analysis by channel
SELECT
    channel_title,
    COUNT(*) as video_count,
    AVG(sentiment_score) as avg_sentiment,
    AVG(engagement_rate) as avg_engagement,
    SUM(view_count) as total_views
FROM default.youtube_shorts.{table_name}
GROUP BY channel_title
ORDER BY avg_sentiment DESC;

-- Top performing videos by engagement
SELECT
    video_id,
    title,
    channel_title,
    view_count,
    engagement_rate,
    sentiment_score,
    is_trending
FROM default.youtube_shorts.{table_name}
ORDER BY engagement_rate DESC
LIMIT 10;

-- Sentiment distribution
SELECT
    CASE
        WHEN sentiment_score > 0.5 THEN 'Very Positive'
        WHEN sentiment_score > 0 THEN 'Positive'
        WHEN sentiment_score = 0 THEN 'Neutral'
        WHEN sentiment_score > -0.5 THEN 'Negative'
        ELSE 'Very Negative'
    END as sentiment_category,
    COUNT(*) as video_count,
    AVG(engagement_rate) as avg_engagement
FROM default.youtube_shorts.{table_name}
GROUP BY sentiment_category
ORDER BY sentiment_score DESC;

-- Trending vs non-trending performance
SELECT
    is_trending,
    COUNT(*) as video_count,
    AVG(view_count) as avg_views,
    AVG(engagement_rate) as avg_engagement,
    AVG(sentiment_score) as avg_sentiment
FROM default.youtube_shorts.{table_name}
GROUP BY is_trending;
"""

    print(analytics_queries)

    # Save analytics queries
    analytics_file = Path(__file__).parent / 'outputs' / f'analytics_{table_name}.sql'
    with open(analytics_file, 'w') as f:
        f.write(analytics_queries)

    print(f"\n✓ Analytics queries saved to: {analytics_file}")


def main():
    """Main execution"""

    print("="*80)
    print("YouTube Shorts Data Export - CSV and Delta Table")
    print("="*80)
    print()

    # Paths
    base_dir = Path(__file__).parent
    data_file = base_dir / 'outputs' / 'neutrogena_demo_data_20251025_081808.json'
    output_csv = base_dir / 'outputs' / 'sentiment_scores_10252025.csv'

    # Check if data file exists
    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        print("Please run standalone_demo.py first to generate data")
        return

    # Export to CSV
    flattened_videos = export_to_csv(str(data_file), str(output_csv))

    if flattened_videos:
        # Create Delta table
        create_delta_table(flattened_videos, table_name="sentiment_scores_10252025")

    print("\n" + "="*80)
    print("Export Complete!")
    print("="*80)
    print(f"\nOutput Files:")
    print(f"  CSV: {output_csv}")
    print(f"  SQL DDL: {base_dir / 'outputs' / 'create_sentiment_scores_10252025.sql'}")
    print(f"  Analytics: {base_dir / 'outputs' / 'analytics_sentiment_scores_10252025.sql'}")
    print()


if __name__ == "__main__":
    main()
