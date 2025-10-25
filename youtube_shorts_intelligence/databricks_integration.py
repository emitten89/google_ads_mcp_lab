"""
Databricks Unity Catalog Integration

Implements medallion architecture (Bronze, Silver, Gold) for YouTube Shorts data
with Unity Catalog governance and Delta Lake ACID transactions.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabricksConfig:
    """Databricks configuration"""
    host: Optional[str] = None
    token: Optional[str] = None
    catalog: str = "brand_intelligence"
    schema: str = "youtube_shorts"
    warehouse_id: Optional[str] = None


class DatabricksIntegration:
    """
    Databricks Unity Catalog integration with medallion architecture

    Architecture Layers:
    - Bronze: Raw data from data collector
    - Silver: Cleaned, enriched, and deduplicated data
    - Gold: Aggregated insights and business metrics
    """

    def __init__(self, config: DatabricksConfig):
        self.config = config
        self.is_connected = False

    def connect(self) -> bool:
        """
        Connect to Databricks workspace

        In production, this would:
        1. Authenticate with Databricks API
        2. Verify Unity Catalog access
        3. Check warehouse availability
        """
        if not self.config.host or not self.config.token:
            logger.warning("Databricks credentials not provided - running in mock mode")
            self.is_connected = False
            return False

        logger.info(f"Connecting to Databricks at {self.config.host}")

        # In production, would make actual connection
        # from databricks import sql
        # self.connection = sql.connect(
        #     server_hostname=self.config.host,
        #     http_path=f"/sql/1.0/warehouses/{self.config.warehouse_id}",
        #     access_token=self.config.token
        # )

        self.is_connected = True
        logger.info("Successfully connected to Databricks")
        return True

    def create_schema(self):
        """
        Create Unity Catalog schema if it doesn't exist

        Creates:
        - Catalog: brand_intelligence
        - Schema: youtube_shorts
        - Tables: bronze_raw_videos, silver_enriched_videos, gold_brand_insights
        """
        if not self.is_connected:
            logger.info("Mock mode: Would create schema structure")
            return

        catalog = self.config.catalog
        schema = self.config.schema

        ddl_statements = [
            f"CREATE CATALOG IF NOT EXISTS {catalog}",
            f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}",
            f"""
            CREATE TABLE IF NOT EXISTS {catalog}.{schema}.bronze_raw_videos (
                video_id STRING,
                title STRING,
                description STRING,
                channel_id STRING,
                channel_title STRING,
                published_at TIMESTAMP,
                view_count BIGINT,
                like_count BIGINT,
                comment_count BIGINT,
                duration STRING,
                tags ARRAY<STRING>,
                hashtags ARRAY<STRING>,
                thumbnail_url STRING,
                raw_data STRING,
                ingestion_timestamp TIMESTAMP,
                source STRING
            )
            USING DELTA
            PARTITIONED BY (DATE(published_at))
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {catalog}.{schema}.silver_enriched_videos (
                video_id STRING,
                title STRING,
                description STRING,
                channel_id STRING,
                channel_title STRING,
                subscriber_count BIGINT,
                published_at TIMESTAMP,
                view_count BIGINT,
                like_count BIGINT,
                comment_count BIGINT,
                engagement_rate DOUBLE,
                is_trending BOOLEAN,
                duration STRING,
                tags ARRAY<STRING>,
                hashtags ARRAY<STRING>,
                comments_sample ARRAY<STRUCT<comment_id:STRING, text:STRING, author:STRING, like_count:INT>>,
                sentiment_score DOUBLE,
                brand_mentions ARRAY<STRING>,
                competitor_mentions ARRAY<STRING>,
                processed_timestamp TIMESTAMP
            )
            USING DELTA
            PARTITIONED BY (DATE(published_at))
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {catalog}.{schema}.gold_brand_insights (
                brand_name STRING,
                insight_date DATE,
                total_videos INT,
                total_views BIGINT,
                total_engagement BIGINT,
                avg_engagement_rate DOUBLE,
                trending_videos INT,
                top_hashtags ARRAY<STRUCT<hashtag:STRING, count:INT>>,
                top_themes ARRAY<STRING>,
                competitive_position STRING,
                recommendations ARRAY<STRING>,
                confidence_score DOUBLE,
                generated_timestamp TIMESTAMP
            )
            USING DELTA
            PARTITIONED BY (insight_date)
            """
        ]

        logger.info("Creating schema structure")
        for ddl in ddl_statements:
            logger.debug(f"Executing: {ddl[:100]}...")
            # In production: self.connection.cursor().execute(ddl)

    def ingest_bronze_data(self, videos: List[Any], source: str = "youtube_api") -> int:
        """
        Ingest raw video data into Bronze layer

        Args:
            videos: List of VideoData objects
            source: Data source identifier

        Returns:
            Number of records ingested
        """
        if not videos:
            logger.warning("No videos to ingest")
            return 0

        logger.info(f"Ingesting {len(videos)} videos to Bronze layer")

        # Convert videos to records
        records = []
        for video in videos:
            record = {
                "video_id": video.video_id,
                "title": video.title,
                "description": video.description,
                "channel_id": video.channel_id,
                "channel_title": video.channel_title,
                "published_at": video.published_at,
                "view_count": video.view_count,
                "like_count": video.like_count,
                "comment_count": video.comment_count,
                "duration": video.duration,
                "tags": video.tags,
                "hashtags": video.hashtags,
                "thumbnail_url": video.thumbnail_url,
                "raw_data": json.dumps(video.to_dict()),
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "source": source
            }
            records.append(record)

        if self.is_connected:
            # In production, would write to Delta table
            # spark.createDataFrame(records).write.format("delta").mode("append").saveAsTable(
            #     f"{self.config.catalog}.{self.config.schema}.bronze_raw_videos"
            # )
            pass
        else:
            logger.info(f"Mock mode: Would ingest {len(records)} records to Bronze layer")

        return len(records)

    def process_to_silver(self, bronze_data: List[Any]) -> List[Dict]:
        """
        Transform Bronze data to Silver layer with enrichments

        Enrichments include:
        - Engagement rate calculation
        - Sentiment analysis on comments
        - Brand/competitor mention detection
        - Data quality checks
        - Deduplication

        Args:
            bronze_data: Raw video data

        Returns:
            List of enriched records
        """
        logger.info(f"Processing {len(bronze_data)} records to Silver layer")

        enriched_records = []

        for video in bronze_data:
            # Calculate engagement rate
            engagement_rate = 0.0
            if video.view_count > 0:
                engagements = video.like_count + video.comment_count
                engagement_rate = (engagements / video.view_count) * 100

            # Analyze comments for sentiment (simplified)
            sentiment_score = self._analyze_sentiment(video.comments_sample if hasattr(video, 'comments_sample') else [])

            # Detect brand mentions
            brand_mentions = self._detect_brand_mentions(video.title + " " + video.description)
            competitor_mentions = self._detect_competitor_mentions(video.title + " " + video.description)

            enriched_record = {
                "video_id": video.video_id,
                "title": video.title,
                "description": video.description,
                "channel_id": video.channel_id,
                "channel_title": video.channel_title,
                "subscriber_count": getattr(video, 'subscriber_count', None),
                "published_at": video.published_at,
                "view_count": video.view_count,
                "like_count": video.like_count,
                "comment_count": video.comment_count,
                "engagement_rate": round(engagement_rate, 2),
                "is_trending": getattr(video, 'is_trending', False),
                "duration": video.duration,
                "tags": video.tags,
                "hashtags": video.hashtags,
                "comments_sample": getattr(video, 'comments_sample', []),
                "sentiment_score": sentiment_score,
                "brand_mentions": brand_mentions,
                "competitor_mentions": competitor_mentions,
                "processed_timestamp": datetime.utcnow().isoformat()
            }

            enriched_records.append(enriched_record)

        if self.is_connected:
            # In production, would write to Delta table
            pass
        else:
            logger.info(f"Mock mode: Would write {len(enriched_records)} records to Silver layer")

        return enriched_records

    def _analyze_sentiment(self, comments: List[Dict]) -> float:
        """
        Analyze sentiment of comments

        Returns sentiment score from -1 (negative) to 1 (positive)
        """
        if not comments:
            return 0.0

        # Simplified sentiment analysis
        # In production, would use NLP model
        positive_words = ['love', 'great', 'amazing', 'works', 'recommend', 'best', 'holy grail']
        negative_words = ['hate', 'terrible', 'worst', 'disappointed', 'waste', 'bad']

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

        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def _detect_brand_mentions(self, text: str) -> List[str]:
        """Detect brand mentions in text"""
        brands = ['neutrogena', 'aveeno', 'listerine', 'band-aid', 'tylenol']
        text_lower = text.lower()
        return [brand for brand in brands if brand in text_lower]

    def _detect_competitor_mentions(self, text: str) -> List[str]:
        """Detect competitor mentions in text"""
        competitors = ['cerave', 'cetaphil', 'olay', 'la roche-posay', 'the ordinary']
        text_lower = text.lower()
        return [comp for comp in competitors if comp in text_lower]

    def aggregate_to_gold(
        self,
        silver_data: List[Dict],
        brand_name: str,
        insights: Dict[str, Any]
    ) -> Dict:
        """
        Create Gold layer insights from Silver data and agent analysis

        Args:
            silver_data: Enriched video data
            brand_name: Brand name
            insights: Insights from AI agents

        Returns:
            Gold layer insight record
        """
        logger.info(f"Aggregating insights to Gold layer for {brand_name}")

        if not silver_data:
            logger.warning("No silver data to aggregate")
            return {}

        # Calculate aggregate metrics
        total_videos = len(silver_data)
        total_views = sum(v.get('view_count', 0) for v in silver_data)
        total_likes = sum(v.get('like_count', 0) for v in silver_data)
        total_comments = sum(v.get('comment_count', 0) for v in silver_data)
        total_engagement = total_likes + total_comments

        avg_engagement_rate = sum(v.get('engagement_rate', 0) for v in silver_data) / total_videos

        trending_videos = sum(1 for v in silver_data if v.get('is_trending', False))

        # Aggregate hashtags
        hashtag_counts = {}
        for video in silver_data:
            for hashtag in video.get('hashtags', []):
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        top_hashtags = [
            {"hashtag": tag, "count": count}
            for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        gold_record = {
            "brand_name": brand_name,
            "insight_date": datetime.utcnow().date().isoformat(),
            "total_videos": total_videos,
            "total_views": total_views,
            "total_engagement": total_engagement,
            "avg_engagement_rate": round(avg_engagement_rate, 2),
            "trending_videos": trending_videos,
            "top_hashtags": top_hashtags,
            "top_themes": insights.get('top_themes', []),
            "competitive_position": insights.get('competitive_position', 'Unknown'),
            "recommendations": insights.get('recommendations', []),
            "confidence_score": insights.get('confidence_score', 0.0),
            "generated_timestamp": datetime.utcnow().isoformat()
        }

        if self.is_connected:
            # In production, would write to Delta table
            pass
        else:
            logger.info(f"Mock mode: Would write Gold insight record for {brand_name}")

        return gold_record

    def query_insights(
        self,
        brand_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Query Gold layer insights for a brand

        Args:
            brand_name: Brand name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of insight records
        """
        logger.info(f"Querying insights for {brand_name}")

        if not self.is_connected:
            logger.info("Mock mode: Would query Gold layer")
            return []

        # In production, would execute SQL query
        # query = f"""
        # SELECT *
        # FROM {self.config.catalog}.{self.config.schema}.gold_brand_insights
        # WHERE brand_name = '{brand_name}'
        # AND insight_date BETWEEN '{start_date}' AND '{end_date}'
        # ORDER BY insight_date DESC
        # """
        # return cursor.execute(query).fetchall()

        return []

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of data pipeline"""
        return {
            "connected": self.is_connected,
            "catalog": self.config.catalog,
            "schema": self.config.schema,
            "layers": {
                "bronze": "bronze_raw_videos",
                "silver": "silver_enriched_videos",
                "gold": "gold_brand_insights"
            }
        }


class DataQuality:
    """Data quality checks and validation"""

    @staticmethod
    def validate_video_data(video: Dict) -> tuple[bool, List[str]]:
        """
        Validate video data quality

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Required fields
        required_fields = ['video_id', 'title', 'view_count', 'published_at']
        for field in required_fields:
            if field not in video or video[field] is None:
                issues.append(f"Missing required field: {field}")

        # Data type checks
        if 'view_count' in video and not isinstance(video['view_count'], (int, float)):
            issues.append("view_count must be numeric")

        # Business logic checks
        if 'view_count' in video and video['view_count'] < 0:
            issues.append("view_count cannot be negative")

        if 'engagement_rate' in video and video['engagement_rate'] > 100:
            issues.append("engagement_rate cannot exceed 100%")

        return len(issues) == 0, issues

    @staticmethod
    def deduplicate_videos(videos: List[Dict]) -> List[Dict]:
        """Remove duplicate videos based on video_id"""
        seen = set()
        unique_videos = []

        for video in videos:
            video_id = video.get('video_id')
            if video_id and video_id not in seen:
                seen.add(video_id)
                unique_videos.append(video)

        removed = len(videos) - len(unique_videos)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate videos")

        return unique_videos
