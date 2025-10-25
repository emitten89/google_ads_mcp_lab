"""
YouTube Shorts Data Collector

Collects data from YouTube Shorts using multiple methods:
1. YouTube Data API v3
2. Web scraping with Playwright
3. Comment analysis
4. Trend detection
5. Competitive monitoring
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoData:
    """Structured data for a YouTube Short"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    tags: List[str]
    hashtags: List[str]
    thumbnail_url: str

    # Enhanced fields from scraping
    subscriber_count: Optional[int] = None
    is_trending: bool = False
    engagement_rate: Optional[float] = None
    comments_sample: List[Dict[str, str]] = None

    # Metadata
    collected_at: str = None
    collection_method: str = "api"

    def __post_init__(self):
        if self.collected_at is None:
            self.collected_at = datetime.utcnow().isoformat()
        if self.comments_sample is None:
            self.comments_sample = []

    def calculate_engagement_rate(self):
        """Calculate engagement rate"""
        if self.view_count > 0:
            engagements = self.like_count + self.comment_count
            self.engagement_rate = (engagements / self.view_count) * 100
        else:
            self.engagement_rate = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class YouTubeDataCollector:
    """Collects YouTube Shorts data via API and web scraping"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.quota_used = 0
        self.quota_limit = 10000

    async def search_shorts(self, keywords: List[str], max_results: int = 50) -> List[VideoData]:
        """
        Search for YouTube Shorts using keywords

        Args:
            keywords: List of search keywords
            max_results: Maximum number of results per keyword

        Returns:
            List of VideoData objects
        """
        logger.info(f"Searching for Shorts with keywords: {keywords}")

        all_videos = []

        for keyword in keywords:
            videos = await self._search_keyword(keyword, max_results)
            all_videos.extend(videos)

        # Remove duplicates based on video_id
        unique_videos = {v.video_id: v for v in all_videos}.values()

        logger.info(f"Found {len(unique_videos)} unique videos")
        return list(unique_videos)

    async def _search_keyword(self, keyword: str, max_results: int) -> List[VideoData]:
        """Search for a single keyword"""

        if self.api_key:
            # Use YouTube API
            videos = await self._search_via_api(keyword, max_results)
        else:
            # Use mock data for demonstration
            videos = self._generate_mock_videos(keyword, max_results)

        return videos

    async def _search_via_api(self, keyword: str, max_results: int) -> List[VideoData]:
        """
        Search using YouTube Data API v3

        This is a placeholder implementation. In production, this would:
        1. Make HTTP request to YouTube API
        2. Handle pagination
        3. Manage quota
        4. Parse response
        """
        logger.info(f"Searching YouTube API for: {keyword}")

        # Quota cost for search.list is 100 units
        quota_cost = 100
        if self.quota_used + quota_cost > self.quota_limit:
            logger.warning("YouTube API quota limit reached")
            return []

        # In production, would make actual API call here
        # For now, return mock data
        videos = self._generate_mock_videos(keyword, min(max_results, 10))

        self.quota_used += quota_cost
        return videos

    def _generate_mock_videos(self, keyword: str, count: int = 10) -> List[VideoData]:
        """Generate mock video data for demonstration"""

        import random
        import hashlib

        videos = []
        base_views = {
            "neutrogena": 150000,
            "skincare": 200000,
            "acne": 180000,
            "hydro boost": 250000,
            "makeup remover": 120000,
        }

        base_view_count = base_views.get(keyword.lower(), 100000)

        for i in range(count):
            # Generate consistent video_id from keyword and index
            video_id = hashlib.md5(f"{keyword}_{i}".encode()).hexdigest()[:11]

            view_count = base_view_count + random.randint(-50000, 100000)
            like_count = int(view_count * random.uniform(0.03, 0.08))
            comment_count = int(view_count * random.uniform(0.001, 0.005))

            video = VideoData(
                video_id=video_id,
                title=f"{keyword.title()} Skincare Routine #{i+1} - Dermatologist Approved",
                description=f"My {keyword} routine that cleared my skin! #skincare #{keyword.replace(' ', '')} #neutrogena",
                channel_id=f"channel_{random.randint(1000, 9999)}",
                channel_title=random.choice([
                    "SkincareByCassandra",
                    "GlowingSkinTips",
                    "DermatologyExperts",
                    "BeautyRoutineDaily",
                    "ClearSkinJourney"
                ]),
                published_at=(datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                duration="PT45S",
                tags=[keyword, "skincare", "beauty", "neutrogena"],
                hashtags=["skincare", keyword.replace(" ", ""), "neutrogena", "beauty"],
                thumbnail_url=f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                subscriber_count=random.randint(10000, 500000),
                is_trending=random.random() > 0.7,
                collection_method="mock"
            )

            video.calculate_engagement_rate()
            videos.append(video)

        return videos

    async def enrich_with_comments(self, videos: List[VideoData], max_comments: int = 100):
        """
        Enrich videos with comment data

        Args:
            videos: List of VideoData objects
            max_comments: Maximum comments to retrieve per video
        """
        logger.info(f"Enriching {len(videos)} videos with comments")

        for video in videos:
            if self.api_key:
                comments = await self._fetch_comments_api(video.video_id, max_comments)
            else:
                comments = self._generate_mock_comments(video.video_id, min(max_comments, 10))

            video.comments_sample = comments

    async def _fetch_comments_api(self, video_id: str, max_comments: int) -> List[Dict[str, str]]:
        """Fetch comments using YouTube API"""

        # Quota cost for commentThreads.list is 1 unit
        quota_cost = 1
        if self.quota_used + quota_cost > self.quota_limit:
            logger.warning("YouTube API quota limit reached")
            return []

        # In production, would make actual API call
        comments = self._generate_mock_comments(video_id, min(max_comments, 10))

        self.quota_used += quota_cost
        return comments

    def _generate_mock_comments(self, video_id: str, count: int = 10) -> List[Dict[str, str]]:
        """Generate mock comments for demonstration"""

        import random

        comment_templates = [
            "This product changed my skin! So glad I tried it",
            "Been using this for 2 weeks and already seeing results",
            "My dermatologist recommended this and it works!",
            "Finally found something that works for my sensitive skin",
            "Love this! The price point is amazing too",
            "This is my holy grail product now",
            "Tried this after seeing your video - game changer!",
            "Does this work for oily skin?",
            "Where can I buy this?",
            "How long did it take to see results?",
        ]

        comments = []
        for i in range(count):
            comments.append({
                "comment_id": f"comment_{video_id}_{i}",
                "text": random.choice(comment_templates),
                "author": f"User{random.randint(1000, 9999)}",
                "like_count": random.randint(0, 500),
                "published_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
            })

        return comments

    async def monitor_channels(self, channel_ids: List[str], days_back: int = 30) -> List[VideoData]:
        """
        Monitor specific channels for new Shorts

        Args:
            channel_ids: List of channel IDs to monitor
            days_back: Number of days to look back

        Returns:
            List of VideoData objects
        """
        logger.info(f"Monitoring {len(channel_ids)} channels")

        all_videos = []

        for channel_id in channel_ids:
            videos = await self._get_channel_shorts(channel_id, days_back)
            all_videos.extend(videos)

        return all_videos

    async def _get_channel_shorts(self, channel_id: str, days_back: int) -> List[VideoData]:
        """Get Shorts from a specific channel"""

        # In production, would use YouTube API to get channel videos
        # filtered by videoDuration=short and publishedAfter

        # For demonstration, generate mock data
        videos = self._generate_mock_videos(f"channel_{channel_id}", count=5)

        return videos

    def save_to_json(self, videos: List[VideoData], output_path: str):
        """Save collected videos to JSON file"""

        data = {
            "metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "video_count": len(videos),
                "quota_used": self.quota_used,
            },
            "videos": [v.to_dict() for v in videos]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(videos)} videos to {output_path}")

    async def collect_competitive_data(
        self,
        brand_keywords: List[str],
        competitor_keywords: List[str],
        max_results_per_keyword: int = 25
    ) -> Dict[str, List[VideoData]]:
        """
        Collect data for both brand and competitors

        Args:
            brand_keywords: Keywords for the brand
            competitor_keywords: Keywords for competitors
            max_results_per_keyword: Max results per keyword

        Returns:
            Dictionary with 'brand' and 'competitors' video lists
        """
        logger.info("Collecting competitive data")

        # Collect brand data
        brand_videos = await self.search_shorts(brand_keywords, max_results_per_keyword)

        # Collect competitor data
        competitor_videos = await self.search_shorts(competitor_keywords, max_results_per_keyword)

        return {
            "brand": brand_videos,
            "competitors": competitor_videos
        }


class TrendAnalyzer:
    """Analyzes trends in YouTube Shorts data"""

    def __init__(self):
        self.trending_threshold = 0.7  # Engagement rate threshold

    def identify_trending_content(self, videos: List[VideoData]) -> List[VideoData]:
        """Identify trending content based on engagement metrics"""

        trending = []

        for video in videos:
            if video.engagement_rate and video.engagement_rate >= self.trending_threshold:
                video.is_trending = True
                trending.append(video)

        logger.info(f"Identified {len(trending)} trending videos")
        return trending

    def analyze_hashtag_trends(self, videos: List[VideoData]) -> Dict[str, int]:
        """Analyze hashtag frequency"""

        hashtag_counts = {}

        for video in videos:
            for hashtag in video.hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        # Sort by frequency
        sorted_hashtags = dict(sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True))

        return sorted_hashtags

    def calculate_aggregate_metrics(self, videos: List[VideoData]) -> Dict[str, Any]:
        """Calculate aggregate metrics across videos"""

        if not videos:
            return {}

        total_views = sum(v.view_count for v in videos)
        total_likes = sum(v.like_count for v in videos)
        total_comments = sum(v.comment_count for v in videos)

        avg_engagement = sum(v.engagement_rate or 0 for v in videos) / len(videos)

        return {
            "video_count": len(videos),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_views": total_views // len(videos),
            "average_engagement_rate": round(avg_engagement, 2),
            "trending_count": sum(1 for v in videos if v.is_trending),
        }


# Main collection function
async def collect_brand_data(
    brand_name: str,
    keywords: List[str],
    competitor_keywords: List[str],
    api_key: Optional[str] = None,
    include_comments: bool = True,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to collect and analyze brand data

    Args:
        brand_name: Name of the brand
        keywords: Brand keywords
        competitor_keywords: Competitor keywords
        api_key: YouTube API key (optional)
        include_comments: Whether to include comment data
        output_path: Path to save JSON output

    Returns:
        Dictionary with collected data and analysis
    """
    collector = YouTubeDataCollector(api_key)
    analyzer = TrendAnalyzer()

    # Collect competitive data
    data = await collector.collect_competitive_data(
        brand_keywords=keywords,
        competitor_keywords=competitor_keywords,
        max_results_per_keyword=25
    )

    brand_videos = data["brand"]
    competitor_videos = data["competitors"]

    # Enrich with comments if requested
    if include_comments:
        await collector.enrich_with_comments(brand_videos)
        await collector.enrich_with_comments(competitor_videos)

    # Analyze trends
    analyzer.identify_trending_content(brand_videos)
    analyzer.identify_trending_content(competitor_videos)

    # Calculate metrics
    brand_metrics = analyzer.calculate_aggregate_metrics(brand_videos)
    competitor_metrics = analyzer.calculate_aggregate_metrics(competitor_videos)

    # Analyze hashtags
    brand_hashtags = analyzer.analyze_hashtag_trends(brand_videos)
    competitor_hashtags = analyzer.analyze_hashtag_trends(competitor_videos)

    result = {
        "brand_name": brand_name,
        "collection_timestamp": datetime.utcnow().isoformat(),
        "brand_videos": brand_videos,
        "competitor_videos": competitor_videos,
        "brand_metrics": brand_metrics,
        "competitor_metrics": competitor_metrics,
        "brand_hashtags": brand_hashtags,
        "competitor_hashtags": competitor_hashtags,
    }

    # Save to file if path provided
    if output_path:
        all_videos = brand_videos + competitor_videos
        collector.save_to_json(all_videos, output_path)

    return result
