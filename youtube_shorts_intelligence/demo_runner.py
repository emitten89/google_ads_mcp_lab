#!/usr/bin/env python3
"""
Production Demo Runner for YouTube Shorts Intelligence Platform

This runner executes the complete production pipeline with live API calls.

Requirements:
    - YouTube Data API key
    - Anthropic API key
    - Databricks workspace credentials

Usage:
    python demo_runner.py --brand neutrogena
    python demo_runner.py --brand kenvue --output-dir ./outputs
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import system_config, BRAND_CONFIGS
from data_collector import collect_brand_data
from databricks_integration import DatabricksIntegration, DatabricksConfig
from agents import AgentOrchestrator


def load_credentials():
    """
    Load API credentials from environment variables

    Required environment variables:
    - YOUTUBE_API_KEY
    - ANTHROPIC_API_KEY
    - DATABRICKS_HOST (optional)
    - DATABRICKS_TOKEN (optional)
    """
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    databricks_host = os.getenv('DATABRICKS_HOST')
    databricks_token = os.getenv('DATABRICKS_TOKEN')

    if not youtube_key:
        print("Warning: YOUTUBE_API_KEY not found. Using mock data.")

    if not anthropic_key:
        print("Warning: ANTHROPIC_API_KEY not found. Using mock agent responses.")

    if not databricks_host or not databricks_token:
        print("Warning: Databricks credentials not found. Running in mock mode.")

    system_config.set_credentials(
        youtube_api_key=youtube_key,
        anthropic_api_key=anthropic_key,
        databricks_host=databricks_host,
        databricks_token=databricks_token
    )

    return {
        'youtube': youtube_key,
        'anthropic': anthropic_key,
        'databricks_host': databricks_host,
        'databricks_token': databricks_token
    }


async def run_intelligence_pipeline(
    brand_name: str,
    output_dir: Path,
    credentials: dict
):
    """
    Execute complete intelligence pipeline

    Args:
        brand_name: Brand name (e.g., 'neutrogena')
        output_dir: Output directory path
        credentials: API credentials dictionary
    """
    print("=" * 80)
    print(f"YOUTUBE SHORTS INTELLIGENCE PIPELINE: {brand_name.upper()}")
    print("=" * 80)
    print(f"Started: {datetime.utcnow().isoformat()}")
    print()

    # Get brand configuration
    try:
        brand_config = system_config.get_brand_config(brand_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Phase 1: Data Collection
    print("PHASE 1: DATA COLLECTION")
    print("-" * 80)

    print(f"Collecting data for {brand_config.name}...")
    print(f"  Keywords: {len(brand_config.keywords)} terms")
    print(f"  Competitors: {len(brand_config.competitors)} brands")
    print(f"  Channels to monitor: {len(brand_config.channels_to_monitor)}")
    print()

    data_output_path = output_dir / f"{brand_name}_data_{timestamp}.json"

    data = await collect_brand_data(
        brand_name=brand_config.name,
        keywords=brand_config.keywords,
        competitor_keywords=brand_config.competitors,
        api_key=credentials['youtube'],
        include_comments=True,
        output_path=str(data_output_path)
    )

    brand_videos = data['brand_videos']
    competitor_videos = data['competitor_videos']
    brand_metrics = data['brand_metrics']
    competitor_metrics = data['competitor_metrics']

    print(f"✓ Collected {len(brand_videos)} brand videos")
    print(f"✓ Collected {len(competitor_videos)} competitor videos")
    print(f"✓ Total views: {brand_metrics['total_views']:,}")
    print(f"✓ Data saved to: {data_output_path}")
    print()

    # Phase 2: Databricks Integration
    print("PHASE 2: DATABRICKS INTEGRATION")
    print("-" * 80)

    databricks_config = DatabricksConfig(
        host=credentials['databricks_host'],
        token=credentials['databricks_token'],
        catalog="brand_intelligence",
        schema="youtube_shorts"
    )

    databricks = DatabricksIntegration(databricks_config)

    if databricks.connect():
        print("✓ Connected to Databricks workspace")

        # Create schema
        databricks.create_schema()
        print("✓ Unity Catalog schema created/verified")

        # Ingest to Bronze
        bronze_count = databricks.ingest_bronze_data(
            videos=brand_videos + competitor_videos,
            source="youtube_api"
        )
        print(f"✓ Ingested {bronze_count} records to Bronze layer")

        # Process to Silver
        silver_data = databricks.process_to_silver(brand_videos)
        print(f"✓ Processed {len(silver_data)} records to Silver layer")
    else:
        print("⚠ Running without Databricks connection")
        silver_data = [v.to_dict() for v in brand_videos]

    print()

    # Phase 3: AI Agent Analysis
    print("PHASE 3: AI AGENT INTELLIGENCE")
    print("-" * 80)

    orchestrator = AgentOrchestrator(api_key=credentials['anthropic'])

    print("Deploying specialized agents...")
    agent_responses = orchestrator.run_all_agents(data)

    print()
    print("Agent Results:")
    for agent_name, response in agent_responses.items():
        print(f"  ✓ {response.agent_name}")
        print(f"    - Insights: {len(response.insights)}")
        print(f"    - Recommendations: {len(response.recommendations)}")
        print(f"    - Confidence: {response.confidence_score:.0%}")

    print()

    # Aggregate insights
    aggregated_insights = orchestrator.aggregate_insights(agent_responses)

    print(f"✓ Aggregated insights from {aggregated_insights['agent_count']} agents")
    print(f"✓ Overall confidence: {aggregated_insights['confidence_score']:.0%}")
    print()

    # Phase 4: Gold Layer Aggregation
    print("PHASE 4: GOLD LAYER INSIGHTS")
    print("-" * 80)

    if databricks.is_connected:
        gold_record = databricks.aggregate_to_gold(
            silver_data=silver_data,
            brand_name=brand_config.name,
            insights=aggregated_insights
        )
        print(f"✓ Created Gold layer insight record")
        print(f"  - Total videos: {gold_record['total_videos']}")
        print(f"  - Total views: {gold_record['total_views']:,}")
        print(f"  - Avg engagement: {gold_record['avg_engagement_rate']:.2f}%")
    else:
        print("⚠ Gold layer creation skipped (no Databricks connection)")

    print()

    # Phase 5: Report Generation
    print("PHASE 5: REPORT GENERATION")
    print("-" * 80)

    report = orchestrator.generate_report(
        agent_responses=agent_responses,
        aggregated_insights=aggregated_insights,
        brand_name=brand_config.name
    )

    report_path = output_dir / f"{brand_name}_report_{timestamp}.txt"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Report generated: {report_path}")

    # Save aggregated insights as JSON
    insights_path = output_dir / f"{brand_name}_insights_{timestamp}.json"
    with open(insights_path, 'w') as f:
        json.dump({
            "brand": brand_config.name,
            "timestamp": timestamp,
            "metrics": {
                "brand": brand_metrics,
                "competitor": competitor_metrics
            },
            "insights": aggregated_insights,
            "agent_responses": {
                name: resp.to_dict()
                for name, resp in agent_responses.items()
            }
        }, f, indent=2)

    print(f"✓ Insights saved: {insights_path}")
    print()

    # Summary
    print("=" * 80)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  Brand: {brand_config.name}")
    print(f"  Videos Analyzed: {len(brand_videos) + len(competitor_videos)}")
    print(f"  Total Views: {brand_metrics['total_views'] + competitor_metrics['total_views']:,}")
    print(f"  Insights Generated: {len(aggregated_insights['all_insights'])}")
    print(f"  Recommendations: {len(aggregated_insights['all_recommendations'])}")
    print(f"  Confidence Score: {aggregated_insights['confidence_score']:.0%}")
    print()
    print("Output Files:")
    print(f"  - Data: {data_output_path}")
    print(f"  - Report: {report_path}")
    print(f"  - Insights: {insights_path}")
    print()

    return {
        "brand": brand_config.name,
        "metrics": brand_metrics,
        "insights": aggregated_insights,
        "output_files": {
            "data": str(data_output_path),
            "report": str(report_path),
            "insights": str(insights_path)
        }
    }


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="YouTube Shorts Intelligence Platform - Production Runner"
    )
    parser.add_argument(
        '--brand',
        type=str,
        default='neutrogena',
        help='Brand name (neutrogena, kenvue, aveeno)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Output directory for results'
    )

    args = parser.parse_args()

    # Load credentials
    credentials = load_credentials()

    # Create output directory
    output_dir = Path(args.output_dir)

    # Run pipeline
    result = asyncio.run(run_intelligence_pipeline(
        brand_name=args.brand,
        output_dir=output_dir,
        credentials=credentials
    ))

    if result:
        print(f"✓ Pipeline completed successfully for {result['brand']}")
    else:
        print("✗ Pipeline execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
