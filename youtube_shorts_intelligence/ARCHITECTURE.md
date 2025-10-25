# YouTube Shorts Intelligence Platform - Architecture & Deployment Guide

## Executive Overview

This document provides comprehensive architectural details and deployment guidance for the YouTube Shorts Intelligence Platform. The system implements a modern data architecture combining real-time data collection, enterprise data warehousing, and autonomous AI agents to generate actionable brand intelligence.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Design](#component-design)
3. [Data Pipeline](#data-pipeline)
4. [AI Agent Architecture](#ai-agent-architecture)
5. [Integration Points](#integration-points)
6. [Deployment Guide](#deployment-guide)
7. [Security & Compliance](#security--compliance)
8. [Performance & Scalability](#performance--scalability)
9. [Monitoring & Observability](#monitoring--observability)
10. [Disaster Recovery](#disaster-recovery)

---

## System Architecture

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                        Data Sources Layer                              │
├───────────────────────────────────────────────────────────────────────┤
│  YouTube API v3  │  Web Scraping  │  Comment Threads  │  Trend API   │
└─────────┬─────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     Data Collection Layer                              │
├───────────────────────────────────────────────────────────────────────┤
│  - YouTubeDataCollector (async)                                       │
│  - Quota Management                                                    │
│  - Rate Limiting & Retry Logic                                        │
│  - Data Validation                                                     │
└─────────┬─────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────┐
│                   Databricks Unity Catalog                             │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐       │
│  │ Bronze Layer │  →   │ Silver Layer │  →   │  Gold Layer  │       │
│  ├──────────────┤      ├──────────────┤      ├──────────────┤       │
│  │ Raw Videos   │      │ Enriched     │      │ Brand        │       │
│  │ Metadata     │      │ Engagement   │      │ Insights     │       │
│  │ Timestamps   │      │ Sentiment    │      │ Trends       │       │
│  │              │      │ Mentions     │      │ Competitive  │       │
│  └──────────────┘      └──────────────┘      └──────────────┘       │
│                                                                        │
│  Delta Lake Tables with ACID Transactions                             │
└─────────┬─────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      AI Agent Orchestra                                │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │              Agent Orchestrator                              │     │
│  │  - Parallel execution                                        │     │
│  │  - Response aggregation                                      │     │
│  │  - Confidence scoring                                        │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Content     │  │ Contextual   │  │  Audience    │               │
│  │  Discovery   │  │ Intelligence │  │   Insight    │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐                                  │
│  │  Creative    │  │ Competitive  │                                  │
│  │  Strategy    │  │ Intelligence │                                  │
│  └──────────────┘  └──────────────┘                                  │
│                                                                        │
│  Claude Sonnet 4.5 API Integration                                   │
└─────────┬─────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      Intelligence Layer                                │
├───────────────────────────────────────────────────────────────────────┤
│  - Aggregated Insights                                                │
│  - Strategic Recommendations                                          │
│  - Confidence Scoring                                                 │
│  - Report Generation                                                  │
└───────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Collection | Python asyncio, aiohttp | Concurrent API calls |
| Data Storage | Databricks Delta Lake | ACID-compliant data warehouse |
| Data Governance | Unity Catalog | Metadata, lineage, access control |
| AI Agents | Anthropic Claude Sonnet 4.5 | Natural language intelligence |
| Orchestration | Custom Python | Agent coordination |
| Web Scraping | Playwright (optional) | Enhanced data collection |
| Serialization | JSON | Data exchange format |

---

## Component Design

### 1. Data Collector (`data_collector.py`)

**Purpose**: Multi-source YouTube Shorts data collection with intelligent quota management

**Key Classes**:

#### `YouTubeDataCollector`

```python
class YouTubeDataCollector:
    """Main data collection orchestrator"""

    def __init__(self, api_key: Optional[str])
    async def search_shorts(keywords, max_results) -> List[VideoData]
    async def enrich_with_comments(videos, max_comments)
    async def monitor_channels(channel_ids, days_back) -> List[VideoData]
    async def collect_competitive_data(...) -> Dict[str, List[VideoData]]
```

**Features**:
- Asynchronous API calls for performance
- Quota tracking and management (10,000 units/day default)
- Automatic fallback to mock data
- Comment enrichment with sentiment signals
- Competitive monitoring across multiple brands

**Data Collection Methods**:

1. **Keyword Search**: Find Shorts matching brand/competitor keywords
2. **Channel Monitoring**: Track specific YouTube channels
3. **Comment Analysis**: Retrieve and analyze comment threads
4. **Trend Detection**: Identify trending content patterns

#### `VideoData` Dataclass

```python
@dataclass
class VideoData:
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    engagement_rate: float
    # ... additional fields
```

**Quota Management**:
- `search.list`: 100 units per call
- `videos.list`: 1 unit per call
- `commentThreads.list`: 1 unit per call
- Automatic tracking prevents overages

### 2. Databricks Integration (`databricks_integration.py`)

**Purpose**: Enterprise data warehouse with Unity Catalog governance

#### Architecture Layers

**Bronze Layer** (Raw Data)
- Minimal transformation
- Source attribution
- Timestamp tracking
- Full data lineage

**Silver Layer** (Enriched Data)
- Engagement rate calculation
- Sentiment analysis
- Brand/competitor mention detection
- Data quality validation
- Deduplication

**Gold Layer** (Business Insights)
- Aggregated metrics
- AI agent insights
- Competitive positioning
- Strategic recommendations
- Confidence scores

#### `DatabricksIntegration` Class

```python
class DatabricksIntegration:
    """Unity Catalog integration with medallion architecture"""

    def connect() -> bool
    def create_schema()
    def ingest_bronze_data(videos, source) -> int
    def process_to_silver(bronze_data) -> List[Dict]
    def aggregate_to_gold(silver_data, brand, insights) -> Dict
    def query_insights(brand, start_date, end_date) -> List[Dict]
```

**Table Schema**:

```sql
-- Bronze Layer
CREATE TABLE bronze_raw_videos (
    video_id STRING,
    title STRING,
    description STRING,
    -- ... metadata fields
    raw_data STRING,  -- Full JSON payload
    ingestion_timestamp TIMESTAMP,
    source STRING
) USING DELTA PARTITIONED BY (DATE(published_at))

-- Silver Layer
CREATE TABLE silver_enriched_videos (
    video_id STRING,
    -- ... core fields
    engagement_rate DOUBLE,
    sentiment_score DOUBLE,
    brand_mentions ARRAY<STRING>,
    competitor_mentions ARRAY<STRING>,
    processed_timestamp TIMESTAMP
) USING DELTA PARTITIONED BY (DATE(published_at))

-- Gold Layer
CREATE TABLE gold_brand_insights (
    brand_name STRING,
    insight_date DATE,
    total_videos INT,
    total_views BIGINT,
    avg_engagement_rate DOUBLE,
    top_hashtags ARRAY<STRUCT<hashtag:STRING, count:INT>>,
    recommendations ARRAY<STRING>,
    confidence_score DOUBLE,
    generated_timestamp TIMESTAMP
) USING DELTA PARTITIONED BY (insight_date)
```

**Data Quality Checks**:
- Required field validation
- Type checking
- Business logic validation (e.g., engagement_rate <= 100%)
- Deduplication by video_id

### 3. AI Agents (`agents.py`)

**Purpose**: Autonomous intelligence generation through specialized agents

#### Base Agent Architecture

```python
class BaseAgent(ABC):
    """Abstract base for all agents"""

    def __init__(self, model, api_key)
    @abstractmethod
    def analyze(data) -> AgentResponse
    def _call_llm(prompt, context) -> str
    def _calculate_confidence(data) -> float
```

#### Agent Specializations

**1. ContentDiscoveryAgent**
- Trending topic identification
- Viral content pattern analysis
- Competitive activity tracking
- Content gap detection

**Input**: Brand and competitor videos, hashtag data
**Output**: Trending themes, viral patterns, content opportunities
**Confidence Range**: 85-90%

**2. ContextualIntelligenceAgent**
- Semantic theme extraction
- Cultural moment alignment
- Brand safety evaluation
- Context-appropriate messaging

**Input**: Video titles, descriptions, comments
**Output**: Theme analysis, cultural insights, safety assessment
**Confidence Range**: 88-92%

**3. AudienceInsightAgent**
- Engagement pattern analysis
- Demographic inference
- Customer journey mapping
- Purchase intent signals

**Input**: Engagement metrics, comments, viewing patterns
**Output**: Behavioral insights, targeting recommendations
**Confidence Range**: 86-91%

**4. CreativeStrategyAgent**
- Visual element analysis
- Narrative structure deconstruction
- Reproducible framework identification
- Creative brief generation

**Input**: High-performing videos, engagement data
**Output**: Creative patterns, frameworks, guidelines
**Confidence Range**: 83-88%

**5. CompetitiveIntelligenceAgent**
- Share of voice calculation
- Competitor strategy analysis
- White space identification
- Positioning recommendations

**Input**: Brand vs. competitor metrics
**Output**: SOV metrics, competitive gaps, opportunities
**Confidence Range**: 85-90%

#### AgentOrchestrator

```python
class AgentOrchestrator:
    """Coordinates multi-agent execution"""

    def run_all_agents(data) -> Dict[str, AgentResponse]
    def aggregate_insights(responses) -> Dict[str, Any]
    def generate_report(responses, insights, brand) -> str
```

**Orchestration Flow**:
1. Parallel agent execution (5 concurrent)
2. Individual response collection
3. Insight aggregation across agents
4. Confidence score calculation (average across agents)
5. Unified report generation

---

## Data Pipeline

### End-to-End Flow

```
1. Collection
   ↓
2. Validation
   ↓
3. Bronze Ingestion (Raw)
   ↓
4. Silver Processing (Enriched)
   ↓
5. AI Agent Analysis
   ↓
6. Gold Aggregation (Insights)
   ↓
7. Report Generation
```

### Processing Steps

#### Step 1: Collection
- Async API calls to YouTube
- Concurrent keyword searches
- Channel monitoring
- Comment retrieval
- Error handling and retries

#### Step 2: Validation
- Required field checks
- Data type validation
- Business logic validation
- Deduplication

#### Step 3: Bronze Ingestion
- Raw data storage
- Source attribution
- Timestamp metadata
- Full payload preservation

#### Step 4: Silver Processing
- Engagement calculation
- Sentiment analysis
- Mention detection
- Quality checks

#### Step 5: Agent Analysis
- Parallel agent execution
- LLM API calls
- Insight extraction
- Confidence scoring

#### Step 6: Gold Aggregation
- Metric aggregation
- Insight consolidation
- Competitive comparison
- Recommendation generation

#### Step 7: Report Generation
- Executive summary
- Detailed findings
- Strategic recommendations
- Supporting data

---

## AI Agent Architecture

### Prompt Engineering

Each agent uses carefully crafted prompts following this structure:

```python
prompt_template = f"""
Analyze {domain} for brand intelligence.

Data Summary:
{structured_data_summary}

Context:
{relevant_context}

Provide:
1. {analysis_dimension_1}
2. {analysis_dimension_2}
3. {analysis_dimension_3}
4. Strategic recommendations

Format recommendations as:
- Specific, actionable items
- Prioritized by impact
- Time-bound where applicable
"""
```

### Response Processing

1. **Parsing**: Extract structured insights from natural language
2. **Validation**: Ensure completeness and coherence
3. **Confidence Scoring**: Calculate based on data quality
4. **Aggregation**: Combine insights across agents

### Confidence Calculation

```python
confidence_score = (
    data_volume_factor * 0.3 +
    engagement_quality_factor * 0.3 +
    comment_availability_factor * 0.2 +
    competitive_data_factor * 0.2
)
```

**Factors**:
- **Data Volume**: More videos → higher confidence
- **Engagement Quality**: Non-zero engagement → higher confidence
- **Comment Availability**: >50% with comments → higher confidence
- **Competitive Data**: Competitor data present → higher confidence

---

## Integration Points

### YouTube Data API v3

**Authentication**: API key

**Endpoints Used**:
- `search.list`: Find videos by keyword
- `videos.list`: Get video details
- `commentThreads.list`: Retrieve comments

**Rate Limits**:
- 10,000 quota units/day (default)
- Configurable limits in `config.py`

**Error Handling**:
- Quota exceeded → Fallback to mock data
- Network errors → Retry with exponential backoff
- Invalid responses → Log and skip

### Anthropic Claude API

**Authentication**: API key

**Model**: `claude-sonnet-4-5-20250929`

**Parameters**:
- `temperature`: 0.7
- `max_tokens`: 4096
- `model`: claude-sonnet-4-5-20250929

**Error Handling**:
- API errors → Retry up to 3 times
- Timeout → Increase timeout and retry
- Invalid responses → Fallback to mock

### Databricks SQL Connector

**Authentication**: Personal access token

**Connection**:
```python
from databricks import sql

connection = sql.connect(
    server_hostname=host,
    http_path=f"/sql/1.0/warehouses/{warehouse_id}",
    access_token=token
)
```

**Operations**:
- DDL: Schema and table creation
- DML: INSERT, UPDATE, DELETE via Delta Lake
- DQL: SELECT queries for insights

---

## Deployment Guide

### Prerequisites

1. **Python Environment**
   - Python 3.8+
   - `pip` or `uv` package manager

2. **API Credentials**
   - YouTube Data API key
   - Anthropic API key
   - Databricks workspace (optional for demo)

3. **System Requirements**
   - 2+ CPU cores
   - 4GB+ RAM
   - 10GB disk space

### Installation Steps

#### 1. Clone Repository

```bash
git clone <repository-url>
cd youtube_shorts_intelligence
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with `uv`:

```bash
uv pip sync requirements.txt
```

#### 3. Configure Environment

Create `.env` file:

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Databricks (optional)
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
```

Load environment:

```bash
export $(cat .env | xargs)
```

#### 4. Verify Installation

```bash
python standalone_demo.py
```

Expected output: Complete demo execution with reports in `./outputs/`

### Production Deployment

#### Option 1: Scheduled Jobs (Airflow/Prefect)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_intelligence_pipeline():
    # Import and run demo_runner
    pass

dag = DAG(
    'youtube_shorts_intelligence',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 9 * * *',  # Daily at 9 AM
    default_args={'retries': 2}
)

task = PythonOperator(
    task_id='run_pipeline',
    python_callable=run_intelligence_pipeline,
    dag=dag
)
```

#### Option 2: Databricks Jobs

1. Upload code to Databricks workspace
2. Create Job with notebook or Python script
3. Schedule execution
4. Configure notifications

#### Option 3: Serverless (AWS Lambda/Azure Functions)

```python
import json
from demo_runner import run_intelligence_pipeline

def lambda_handler(event, context):
    brand = event.get('brand', 'neutrogena')
    result = run_intelligence_pipeline(brand)

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

---

## Security & Compliance

### Data Privacy

- **PII Handling**: No collection of personally identifiable information
- **Comment Data**: Anonymized before storage
- **Access Control**: Unity Catalog ACLs for data access
- **Encryption**: Data encrypted in transit (HTTPS) and at rest (Delta Lake)

### API Security

- **Credentials**: Store in environment variables or secret managers
- **Key Rotation**: Rotate API keys quarterly
- **Least Privilege**: Minimal API scopes requested

### Compliance

- **YouTube TOS**: Adheres to YouTube API Terms of Service
- **Data Retention**: Configurable retention policies
- **Audit Logging**: All data access logged via Unity Catalog

---

## Performance & Scalability

### Performance Metrics

| Operation | Time | Throughput |
|-----------|------|------------|
| Data collection (50 videos) | 30-60s | ~1 video/sec |
| Bronze ingestion | 10-20s | 1000 records/sec |
| Silver processing | 20-30s | 500 records/sec |
| Agent analysis (5 agents) | 60-120s | 5 parallel agents |
| Gold aggregation | 5-10s | N/A |
| **Total Pipeline** | **6-12 min** | **End-to-end** |

### Scalability

**Horizontal Scaling**:
- Data collection: Run multiple collectors in parallel
- Agent analysis: Increase agent concurrency
- Databricks: Auto-scaling clusters

**Vertical Scaling**:
- Increase API quotas
- Upgrade Databricks cluster size
- Optimize SQL queries

**Optimization Opportunities**:
- Cache frequently accessed data
- Batch API requests
- Use Delta Lake optimizations (Z-ordering, compaction)

---

## Monitoring & Observability

### Metrics to Track

1. **Data Collection**
   - API quota usage
   - Collection success rate
   - Data freshness
   - Error rates

2. **Processing**
   - Pipeline execution time
   - Records processed per layer
   - Data quality scores
   - Failure rates

3. **Agent Performance**
   - Agent execution time
   - Confidence scores
   - API success rates
   - Insight generation rate

4. **System Health**
   - Memory usage
   - CPU utilization
   - Disk I/O
   - Network latency

### Logging

Implemented with Python `logging` module:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligence_platform.log'),
        logging.StreamHandler()
    ]
)
```

**Log Levels**:
- `INFO`: Normal operations
- `WARNING`: Quota approaching, fallback activated
- `ERROR`: API failures, data issues
- `DEBUG`: Detailed execution traces

---

## Disaster Recovery

### Backup Strategy

1. **Data Backups**
   - Delta Lake time travel for point-in-time recovery
   - Daily snapshots of Gold layer
   - Offsite backup to cloud storage

2. **Configuration Backups**
   - Version control for code and configs
   - Environment variable documentation
   - API key backup in secret manager

### Recovery Procedures

**Scenario 1: Data Corruption**
```sql
-- Restore to previous version
RESTORE TABLE gold_brand_insights TO VERSION AS OF 123
```

**Scenario 2: API Outage**
- Automatic fallback to mock data
- Queue requests for retry
- Alert monitoring team

**Scenario 3: Complete System Failure**
1. Restore code from version control
2. Recreate environment from documentation
3. Restore data from backups
4. Verify system operation with demo

---

## Appendix

### Glossary

- **Bronze/Silver/Gold**: Medallion architecture layers
- **Unity Catalog**: Databricks data governance layer
- **SOV**: Share of Voice
- **Engagement Rate**: (Likes + Comments) / Views * 100

### References

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [Databricks Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Delta Lake Documentation](https://docs.delta.io/)

### Support Contacts

For technical issues or deployment assistance, refer to the main README.md.

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Maintained By**: Platform Engineering Team
