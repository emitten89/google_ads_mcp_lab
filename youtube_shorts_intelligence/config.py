"""
Configuration for YouTube Shorts Intelligence Platform

Defines brand configurations for Neutrogena, Kenvue, and other brands
with keywords, competitors, and target demographics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class BrandConfig:
    """Configuration for a specific brand"""
    name: str
    keywords: List[str]
    competitors: List[str]
    target_demographics: Dict[str, any]
    channels_to_monitor: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate configuration"""
        if not self.name:
            raise ValueError("Brand name is required")
        if not self.keywords:
            raise ValueError("At least one keyword is required")


# Neutrogena Brand Configuration
NEUTROGENA_CONFIG = BrandConfig(
    name="Neutrogena",
    keywords=[
        "neutrogena",
        "neutrogena skincare",
        "hydro boost",
        "neutrogena acne",
        "neutrogena makeup remover",
        "neutrogena sunscreen",
        "neutrogena face wash",
        "neutrogena retinol",
        "dermatologist recommended",
        "clinical skincare",
    ],
    competitors=[
        "CeraVe",
        "La Roche-Posay",
        "Cetaphil",
        "Olay",
        "Aveeno",
        "Garnier",
        "The Ordinary",
        "Paula's Choice",
    ],
    target_demographics={
        "age_range": "18-45",
        "gender": "primarily female, expanding to all genders",
        "interests": ["skincare", "beauty", "wellness", "dermatology"],
        "pain_points": [
            "acne",
            "dry skin",
            "sensitive skin",
            "anti-aging",
            "sun protection",
            "affordable clinical skincare"
        ]
    },
    channels_to_monitor=[
        "@Neutrogena",
        "@CeraVe",
        "@LaRochePosayUSA",
        "@Cetaphil",
        "@Olay",
        "@TheOrdinarySkincare",
    ],
    content_themes=[
        "product reviews",
        "skincare routines",
        "before and after",
        "dermatologist reactions",
        "ingredient education",
        "skin concerns solutions",
        "seasonal skincare tips",
    ]
)


# Kenvue Portfolio Configuration
KENVUE_CONFIG = BrandConfig(
    name="Kenvue",
    keywords=[
        "kenvue",
        "johnson and johnson consumer",
        "band-aid",
        "listerine",
        "tylenol",
        "zyrtec",
        "motrin",
        "benadryl",
        "nicorette",
        "visine",
    ],
    competitors=[
        "Procter & Gamble",
        "Unilever",
        "Beiersdorf",
        "Reckitt Benckiser",
        "GSK Consumer Healthcare",
        "Bayer Consumer Health",
    ],
    target_demographics={
        "age_range": "25-65",
        "gender": "all genders",
        "interests": ["health", "wellness", "family care", "personal care"],
        "pain_points": [
            "pain relief",
            "allergies",
            "oral health",
            "wound care",
            "smoking cessation",
            "eye care",
        ]
    },
    channels_to_monitor=[
        "@Neutrogena",
        "@Aveeno",
        "@Listerine",
        "@BANDAID",
        "@TYLENOL",
    ],
    content_themes=[
        "health education",
        "product demonstrations",
        "expert recommendations",
        "lifestyle wellness",
        "family care moments",
        "trusted brands heritage",
    ]
)


# Additional Brand Configurations (expandable)
AVEENO_CONFIG = BrandConfig(
    name="Aveeno",
    keywords=[
        "aveeno",
        "aveeno oat",
        "colloidal oatmeal",
        "aveeno eczema",
        "aveeno baby",
        "aveeno daily moisturizer",
        "sensitive skin",
        "natural ingredients",
    ],
    competitors=[
        "Cetaphil",
        "Eucerin",
        "Vanicream",
        "Aquaphor",
    ],
    target_demographics={
        "age_range": "25-55",
        "gender": "all genders, focus on parents",
        "interests": ["natural skincare", "sensitive skin", "baby care", "eczema solutions"],
        "pain_points": [
            "eczema",
            "dry skin",
            "sensitive skin",
            "baby skincare",
            "natural ingredients preference",
        ]
    },
    channels_to_monitor=[
        "@Aveeno",
        "@Cetaphil",
        "@Eucerin",
    ],
    content_themes=[
        "oat-based skincare",
        "eczema care",
        "baby skincare",
        "natural ingredients",
        "dermatologist approved",
    ]
)


# Configuration Registry
BRAND_CONFIGS = {
    "neutrogena": NEUTROGENA_CONFIG,
    "kenvue": KENVUE_CONFIG,
    "aveeno": AVEENO_CONFIG,
}


# API Configuration
@dataclass
class APIConfig:
    """API configuration settings"""
    youtube_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    databricks_host: Optional[str] = None
    databricks_token: Optional[str] = None

    # Rate limiting
    youtube_quota_limit: int = 10000
    max_videos_per_query: int = 50
    max_comments_per_video: int = 100

    # Scraping configuration
    scraping_timeout: int = 30
    scraping_max_retries: int = 3

    # Agent configuration
    agent_model: str = "claude-sonnet-4-5-20250929"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096


# Data Pipeline Configuration
@dataclass
class DataPipelineConfig:
    """Data pipeline configuration"""
    # Bronze layer (raw data)
    bronze_path: str = "bronze/youtube_shorts"

    # Silver layer (cleaned and enriched)
    silver_path: str = "silver/youtube_shorts_enriched"

    # Gold layer (aggregated insights)
    gold_path: str = "gold/brand_intelligence"

    # Unity Catalog
    catalog_name: str = "brand_intelligence"
    schema_name: str = "youtube_shorts"

    # Table names
    raw_videos_table: str = "raw_videos"
    enriched_videos_table: str = "enriched_videos"
    insights_table: str = "brand_insights"
    trends_table: str = "content_trends"


# System Configuration
class SystemConfig:
    """Global system configuration"""

    def __init__(self):
        self.api = APIConfig()
        self.pipeline = DataPipelineConfig()

    def set_credentials(
        self,
        youtube_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        databricks_host: Optional[str] = None,
        databricks_token: Optional[str] = None,
    ):
        """Set API credentials"""
        if youtube_api_key:
            self.api.youtube_api_key = youtube_api_key
        if anthropic_api_key:
            self.api.anthropic_api_key = anthropic_api_key
        if databricks_host:
            self.api.databricks_host = databricks_host
        if databricks_token:
            self.api.databricks_token = databricks_token

    def get_brand_config(self, brand_name: str) -> BrandConfig:
        """Get configuration for a specific brand"""
        brand_key = brand_name.lower()
        if brand_key not in BRAND_CONFIGS:
            raise ValueError(f"Unknown brand: {brand_name}. Available brands: {list(BRAND_CONFIGS.keys())}")
        return BRAND_CONFIGS[brand_key]


# Default system configuration
system_config = SystemConfig()
