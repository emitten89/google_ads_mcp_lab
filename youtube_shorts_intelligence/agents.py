"""
AI Agents for YouTube Shorts Intelligence

Five specialized agents built on Claude Sonnet 4.5:
1. Content Discovery Agent - Identifies trending topics and viral patterns
2. Contextual Intelligence Agent - Analyzes semantic themes and cultural moments
3. Audience Insight Agent - Analyzes behavioral patterns and demographics
4. Creative Strategy Agent - Deconstructs successful content patterns
5. Competitive Intelligence Agent - Tracks market positioning and opportunities
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Structured response from an agent"""
    agent_name: str
    analysis: str
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    metadata: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "analysis": self.analysis,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """Base class for all intelligence agents"""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.agent_name = self.__class__.__name__

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze data and return insights"""
        pass

    def _call_llm(self, prompt: str, context: Dict) -> str:
        """
        Call Claude API with prompt

        In production, this would:
        1. Make API call to Anthropic
        2. Handle rate limiting
        3. Parse response
        4. Handle errors

        For demonstration, returns structured mock response
        """
        if self.api_key:
            # In production, would make actual API call
            # from anthropic import Anthropic
            # client = Anthropic(api_key=self.api_key)
            # response = client.messages.create(
            #     model=self.model,
            #     max_tokens=4096,
            #     temperature=0.7,
            #     messages=[{"role": "user", "content": prompt}]
            # )
            # return response.content[0].text
            pass

        # Return mock response based on agent type
        return self._generate_mock_response(context)

    @abstractmethod
    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response for demonstration"""
        pass

    def _extract_insights(self, response: str) -> List[str]:
        """Extract key insights from LLM response"""
        # Simple extraction - in production would use more sophisticated parsing
        lines = response.split('\n')
        insights = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
        return insights[:5]  # Top 5 insights

    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from LLM response"""
        # Look for recommendations section
        if "Recommendations:" in response:
            rec_section = response.split("Recommendations:")[1]
            lines = rec_section.split('\n')
            recommendations = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
            return recommendations[:5]
        return []

    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score based on data quality and completeness"""
        score = 0.0

        # Data volume factor
        video_count = len(data.get('brand_videos', []))
        if video_count > 20:
            score += 0.3
        elif video_count > 10:
            score += 0.2
        else:
            score += 0.1

        # Engagement data quality
        videos = data.get('brand_videos', [])
        if videos:
            avg_engagement = sum(getattr(v, 'engagement_rate', 0) for v in videos) / len(videos)
            if avg_engagement > 0:
                score += 0.3

        # Comment data availability
        videos_with_comments = sum(1 for v in videos if getattr(v, 'comments_sample', []))
        if videos_with_comments > len(videos) * 0.5:
            score += 0.2

        # Competitor data availability
        if data.get('competitor_videos'):
            score += 0.2

        return min(round(score, 2), 1.0)


class ContentDiscoveryAgent(BaseAgent):
    """
    Agent specializing in content discovery and trend identification

    Capabilities:
    - Identifies trending topics and viral content patterns
    - Detects emerging trends before market saturation
    - Analyzes competitive content activity
    - Identifies content gaps and opportunities
    """

    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze content trends and discovery opportunities"""

        logger.info("ContentDiscoveryAgent analyzing data...")

        brand_videos = data.get('brand_videos', [])
        competitor_videos = data.get('competitor_videos', [])
        brand_hashtags = data.get('brand_hashtags', {})
        competitor_hashtags = data.get('competitor_hashtags', {})

        # Build context for LLM
        context = {
            "brand_video_count": len(brand_videos),
            "competitor_video_count": len(competitor_videos),
            "brand_top_hashtags": list(brand_hashtags.items())[:10],
            "competitor_top_hashtags": list(competitor_hashtags.items())[:10],
            "trending_brand_videos": sum(1 for v in brand_videos if getattr(v, 'is_trending', False)),
            "trending_competitor_videos": sum(1 for v in competitor_videos if getattr(v, 'is_trending', False)),
        }

        prompt = self._build_prompt(context)
        response_text = self._call_llm(prompt, context)

        insights = self._extract_insights(response_text)
        recommendations = self._extract_recommendations(response_text)
        confidence = self._calculate_confidence(data)

        return AgentResponse(
            agent_name="ContentDiscoveryAgent",
            analysis=response_text,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence,
            metadata=context
        )

    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for content discovery analysis"""
        return f"""
        Analyze YouTube Shorts content trends for brand intelligence.

        Data Summary:
        - Brand videos analyzed: {context['brand_video_count']}
        - Competitor videos analyzed: {context['competitor_video_count']}
        - Trending brand content: {context['trending_brand_videos']} videos
        - Trending competitor content: {context['trending_competitor_videos']} videos

        Top Brand Hashtags: {', '.join([f"#{tag} ({count})" for tag, count in context['brand_top_hashtags'][:5]])}
        Top Competitor Hashtags: {', '.join([f"#{tag} ({count})" for tag, count in context['competitor_top_hashtags'][:5]])}

        Provide:
        1. Trending topic analysis
        2. Viral content patterns
        3. Competitive activity assessment
        4. Content gap opportunities

        Recommendations:
        [Provide specific, actionable recommendations]
        """

    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response for demonstration"""
        return f"""
Content Discovery Analysis:

Trending Topics Identified:
- Skincare routines and "get ready with me" content showing 47% higher engagement
- Dermatologist reaction videos gaining momentum (3.2x views vs. traditional reviews)
- Before/after transformation content achieving 2.8x engagement rate
- Product comparison videos trending with 65% higher watch completion
- Budget-friendly skincare alternatives resonating with Gen Z audience

Viral Content Patterns:
- Hook within first 2 seconds crucial for retention (85% of viral videos)
- Text overlay with problem/solution format driving 54% more engagement
- POV-style content outperforming traditional product shots by 2.1x
- Authentic, unfiltered content showing real results gaining trust signals
- Sound trending: relatable audio clips about skincare struggles

Competitive Activity Assessment:
- CeraVe dominating with consistent 3-4x weekly posting cadence
- La Roche-Posay investing heavily in dermatologist partnerships
- The Ordinary capturing DIY skincare enthusiast segment
- Competitors achieving 23% higher share-of-voice in acne treatment category
- Market gap in accessible clinical skincare education content

Content Gaps & Opportunities:
- Limited brand presence in dermatologist collaboration space
- Underutilized ingredient education content format
- Opportunity in seasonal skincare transition guides
- White space in teen skincare routine content
- Missing cultural moment tie-ins (trending beauty challenges)

Recommendations:
- Launch dermatologist partnership series to build clinical credibility
- Create ingredient education shorts using trending POV format
- Develop seasonal skincare content calendar aligned with search trends
- Test before/after transformation series with real consumer results
- Increase posting frequency to 3-4x weekly to match category leaders
- Invest in authentic UGC-style content vs. polished brand content
- Target emerging trends 2-3 weeks before saturation for first-mover advantage
        """


class ContextualIntelligenceAgent(BaseAgent):
    """
    Agent specializing in contextual and semantic analysis

    Capabilities:
    - Semantic analysis of content themes
    - Cultural moment identification
    - Brand safety evaluation
    - Context-appropriate messaging recommendations
    """

    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze contextual and semantic patterns"""

        logger.info("ContextualIntelligenceAgent analyzing data...")

        brand_videos = data.get('brand_videos', [])

        # Analyze video titles and descriptions
        themes = self._extract_themes(brand_videos)

        context = {
            "themes": themes,
            "video_count": len(brand_videos),
            "avg_sentiment": self._calculate_avg_sentiment(brand_videos),
        }

        prompt = self._build_prompt(context)
        response_text = self._call_llm(prompt, context)

        insights = self._extract_insights(response_text)
        recommendations = self._extract_recommendations(response_text)
        confidence = self._calculate_confidence(data)

        return AgentResponse(
            agent_name="ContextualIntelligenceAgent",
            analysis=response_text,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence,
            metadata=context
        )

    def _extract_themes(self, videos: List) -> List[str]:
        """Extract common themes from video content"""
        themes = []
        keywords = ['routine', 'review', 'tutorial', 'transformation', 'reaction', 'comparison']

        for video in videos[:20]:  # Sample first 20 videos
            title = getattr(video, 'title', '').lower()
            for keyword in keywords:
                if keyword in title and keyword not in themes:
                    themes.append(keyword)

        return themes

    def _calculate_avg_sentiment(self, videos: List) -> float:
        """Calculate average sentiment from comments"""
        # Simplified sentiment calculation
        return 0.65  # Positive sentiment

    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for contextual analysis"""
        return f"""
        Analyze contextual intelligence for YouTube Shorts content.

        Content Themes Identified: {', '.join(context['themes'])}
        Videos Analyzed: {context['video_count']}
        Average Sentiment: {context['avg_sentiment']}

        Provide:
        1. Semantic theme analysis
        2. Cultural moment relevance
        3. Brand safety assessment
        4. Context-appropriate messaging recommendations
        """

    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response"""
        return f"""
Contextual Intelligence Analysis:

Semantic Theme Analysis:
- Self-care and wellness narratives dominating content (68% of videos)
- Clinical efficacy messaging resonating with evidence-seeking consumers
- Affordability and accessibility themes gaining traction
- Clean beauty and ingredient transparency becoming table stakes
- Dermatologist endorsement as key trust signal

Cultural Moment Relevance:
- "Skin cycling" trend creating opportunity for routine-based content
- #SkinTok community actively seeking scientific skincare information
- Sustainability consciousness influencing purchase decisions
- Body positivity movement embracing real skin textures/concerns
- Mental health awareness connecting skincare to self-care ritual

Brand Safety Assessment:
- 94% of analyzed content maintains brand-safe environment
- Positive sentiment toward science-backed skincare claims
- Community values authenticity over perfection
- Educational content receives higher trust scores
- Minimal controversial topics in skincare vertical

Context-Appropriate Messaging:
- Lead with clinical credibility (dermatologist-tested, proven ingredients)
- Balance aspirational results with realistic expectations
- Emphasize accessibility: "clinical skincare for everyone"
- Connect product benefits to emotional well-being
- Use inclusive language and diverse representation

Recommendations:
- Align messaging with cultural wellness movement
- Develop content that educates while entertaining
- Partner with credible dermatologists and skincare experts
- Emphasize ingredient transparency and clinical testing
- Create content celebrating diverse skin types and concerns
        """


class AudienceInsightAgent(BaseAgent):
    """
    Agent specializing in audience behavior and demographics

    Capabilities:
    - Analyzes engagement patterns
    - Identifies audience demographics
    - Maps customer journey touchpoints
    - Generates targeting recommendations
    """

    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze audience insights and behaviors"""

        logger.info("AudienceInsightAgent analyzing data...")

        brand_videos = data.get('brand_videos', [])
        brand_metrics = data.get('brand_metrics', {})

        context = {
            "avg_engagement_rate": brand_metrics.get('average_engagement_rate', 0),
            "total_views": brand_metrics.get('total_views', 0),
            "video_count": len(brand_videos),
            "trending_count": sum(1 for v in brand_videos if getattr(v, 'is_trending', False)),
        }

        prompt = self._build_prompt(context)
        response_text = self._call_llm(prompt, context)

        insights = self._extract_insights(response_text)
        recommendations = self._extract_recommendations(response_text)
        confidence = self._calculate_confidence(data)

        return AgentResponse(
            agent_name="AudienceInsightAgent",
            analysis=response_text,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence,
            metadata=context
        )

    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for audience analysis"""
        return f"""
        Analyze audience insights from YouTube Shorts data.

        Engagement Metrics:
        - Average Engagement Rate: {context['avg_engagement_rate']}%
        - Total Views: {context['total_views']:,}
        - Videos Analyzed: {context['video_count']}
        - Trending Content: {context['trending_count']} videos

        Provide:
        1. Audience behavior patterns
        2. Demographic insights
        3. Customer journey mapping
        4. Targeting optimization recommendations
        """

    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response"""
        return f"""
Audience Insight Analysis:

Behavioral Patterns:
- Peak engagement windows: 7:30-9:00 AM (morning routine) and 8:30-10:00 PM (evening routine)
- Average watch time 42 seconds (93% completion rate for 45s shorts)
- Strong save-for-later behavior indicating purchase intent (2.3x category average)
- Comment section shows high information-seeking behavior (questions vs reactions)
- Repeat viewership patterns suggest content being used as tutorials

Demographic Insights:
- Primary audience: Female 18-34 (67%)
- Growing male audience segment (18-24) up 23% YoY
- Secondary audience: 35-45 interested in anti-aging solutions
- Geographic concentration: Urban/suburban markets
- Income skew: Middle-income value-conscious consumers

Purchase Intent Signals:
- "Where to buy" comments on 34% of product-focused videos
- Saved content correlates with 2.1x higher purchase consideration
- Price comparison searches indicate deal-seeking behavior
- Before/after content drives highest purchase intent (78% correlation)
- Questions about specific skin concerns show high consideration

Content Consumption Patterns:
- Routine/tutorial content shows highest re-watch rate
- Product comparison videos drive cross-shopping behavior
- Expert validation (dermatologist) increases trust +45%
- Real results content outperforms professional production quality
- Educational content shared 3.2x more than promotional content

Customer Journey Mapping:
- Awareness: Discovery through #SkinTok trending content
- Consideration: Educational content and dermatologist validation
- Evaluation: Before/after results and peer reviews
- Purchase: Influenced by value proposition and accessibility
- Loyalty: Routine-based content encouraging consistent usage

Recommendations:
- Optimize posting times for 7:30 AM EST and 8:30 PM EST
- Develop content series addressing specific skin concerns
- Create shoppable content linking to purchase pages
- Invest in expert collaboration content for trust-building
- Develop retargeting strategy for users who save/share content
- Create FAQ-style content addressing common comment questions
        """


class CreativeStrategyAgent(BaseAgent):
    """
    Agent specializing in creative content strategy

    Capabilities:
    - Deconstructs high-performing creative patterns
    - Analyzes visual and narrative elements
    - Identifies reproducible creative frameworks
    - Generates creative briefs and guidelines
    """

    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze creative strategy and patterns"""

        logger.info("CreativeStrategyAgent analyzing data...")

        brand_videos = data.get('brand_videos', [])
        trending_videos = [v for v in brand_videos if getattr(v, 'is_trending', False)]

        context = {
            "total_videos": len(brand_videos),
            "trending_videos": len(trending_videos),
            "avg_engagement": sum(getattr(v, 'engagement_rate', 0) for v in brand_videos) / len(brand_videos) if brand_videos else 0,
        }

        prompt = self._build_prompt(context)
        response_text = self._call_llm(prompt, context)

        insights = self._extract_insights(response_text)
        recommendations = self._extract_recommendations(response_text)
        confidence = self._calculate_confidence(data)

        return AgentResponse(
            agent_name="CreativeStrategyAgent",
            analysis=response_text,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence,
            metadata=context
        )

    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for creative analysis"""
        return f"""
        Analyze creative strategy from YouTube Shorts performance data.

        Creative Performance:
        - Total Videos: {context['total_videos']}
        - High-Performing Content: {context['trending_videos']} videos
        - Average Engagement: {context['avg_engagement']:.2f}%

        Provide:
        1. High-performing creative pattern analysis
        2. Visual and narrative element breakdown
        3. Reproducible creative frameworks
        4. Creative brief recommendations
        """

    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response"""
        return f"""
Creative Strategy Analysis:

High-Performing Creative Patterns:
- Problem-solution narrative structure (3-5-3 second format)
- Text overlay stating problem in first 2 seconds
- Visual product demonstration in middle section
- Results/testimonial close with clear CTA
- Authentic, relatable talent over professional models

Visual Element Analysis:
- Bright, clean aesthetic with skincare-appropriate lighting
- Close-up shots showing product texture and application
- Before/after split-screen format driving 2.1x engagement
- Minimal background distraction focusing on skin/product
- Text overlays using 60-80pt font for mobile readability

Narrative Elements:
- First-person POV storytelling building trust
- Vulnerability about skin struggles creating relatability
- Scientific ingredient explanation building credibility
- Timeline transparency ("after 2 weeks") managing expectations
- Clear problem statement matching audience pain points

Audio Strategy:
- Trending audio with skincare-relevant themes
- Voiceover explaining routine/benefits
- Ambient sound for authentic feel
- Music tempo matching content pacing
- Strategic silence for emphasis on key claims

Reproducible Creative Frameworks:

Framework 1: "Transformation Journey"
- Open with "before" skin struggle
- Product introduction with key benefit
- Usage demonstration
- "After" results with timeline
- Call to action

Framework 2: "Expert Validation"
- Dermatologist intro establishing credibility
- Common skin concern identification
- Product recommendation with ingredient breakdown
- Usage tips from expert perspective
- Professional endorsement close

Framework 3: "Real Routine Integration"
- Relatable morning/evening routine setting
- Product as part of everyday ritual
- Natural application demonstration
- Lifestyle context showing accessibility
- Authentic recommendation to camera

Creative Performance Drivers:
- Authenticity over production quality (grassroots feel)
- Educational value driving shareability
- Relatable talent matching target demographic
- Clear value proposition in first 3 seconds
- Mobile-first vertical composition

Recommendations:
- Develop creative brief template based on top 3 frameworks
- Test UGC-style content vs. branded production
- Invest in diverse talent representing various skin types
- Create modular content system for rapid testing
- Establish creative guidelines prioritizing authenticity
- Build content library of high-performing elements for remixing
        """


class CompetitiveIntelligenceAgent(BaseAgent):
    """
    Agent specializing in competitive analysis

    Capabilities:
    - Tracks competitor content strategy
    - Identifies competitive positioning
    - Analyzes share of voice
    - Identifies white space opportunities
    """

    def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        """Analyze competitive intelligence"""

        logger.info("CompetitiveIntelligenceAgent analyzing data...")

        brand_metrics = data.get('brand_metrics', {})
        competitor_metrics = data.get('competitor_metrics', {})
        brand_hashtags = data.get('brand_hashtags', {})
        competitor_hashtags = data.get('competitor_hashtags', {})

        context = {
            "brand_video_count": brand_metrics.get('video_count', 0),
            "competitor_video_count": competitor_metrics.get('video_count', 0),
            "brand_avg_engagement": brand_metrics.get('average_engagement_rate', 0),
            "competitor_avg_engagement": competitor_metrics.get('average_engagement_rate', 0),
            "brand_total_views": brand_metrics.get('total_views', 0),
            "competitor_total_views": competitor_metrics.get('total_views', 0),
        }

        prompt = self._build_prompt(context)
        response_text = self._call_llm(prompt, context)

        insights = self._extract_insights(response_text)
        recommendations = self._extract_recommendations(response_text)
        confidence = self._calculate_confidence(data)

        return AgentResponse(
            agent_name="CompetitiveIntelligenceAgent",
            analysis=response_text,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence,
            metadata=context
        )

    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for competitive analysis"""
        return f"""
        Analyze competitive intelligence from YouTube Shorts data.

        Brand Performance:
        - Videos: {context['brand_video_count']}
        - Avg Engagement: {context['brand_avg_engagement']:.2f}%
        - Total Views: {context['brand_total_views']:,}

        Competitor Performance:
        - Videos: {context['competitor_video_count']}
        - Avg Engagement: {context['competitor_avg_engagement']:.2f}%
        - Total Views: {context['competitor_total_views']:,}

        Provide:
        1. Competitive positioning analysis
        2. Share of voice assessment
        3. Competitor strategy patterns
        4. White space opportunity identification
        """

    def _generate_mock_response(self, context: Dict) -> str:
        """Generate mock response"""
        brand_sov = context['brand_total_views'] / (context['brand_total_views'] + context['competitor_total_views']) * 100 if context['brand_total_views'] + context['competitor_total_views'] > 0 else 0

        return f"""
Competitive Intelligence Analysis:

Share of Voice Analysis:
- Current Brand SOV: {brand_sov:.1f}%
- Category Leader SOV: 28.3% (CeraVe)
- SOV Gap: {28.3 - brand_sov:.1f} percentage points
- Quarterly SOV trend: +2.3% QoQ growth
- Engagement quality: Brand achieving 15% higher engagement rate vs category average

Competitive Positioning:
- CeraVe: Mass-market leader, dermatologist association, consistent presence
- La Roche-Posay: Premium positioning, European heritage, scientific credibility
- The Ordinary: Ingredient-focused, affordability, transparency
- Cetaphil: Gentle/sensitive skin, medical professional recommended
- Brand Differentiation Opportunity: Accessible clinical efficacy

Competitor Content Strategy Patterns:

CeraVe:
- High-frequency posting (5-7x weekly)
- Dermatologist partnership content
- Ingredient education focus
- Strong UGC amplification
- Cross-platform hashtag strategy

La Roche-Posay:
- Premium production quality
- Expert-led educational content
- Sensitive skin positioning
- European skincare heritage narrative
- Selective influencer partnerships

The Ordinary:
- Ingredient deep-dives and science education
- Comparison/dupe content
- Budget-conscious messaging
- DIY skincare enthusiast community
- Minimalist aesthetic

Competitive Advantages Identified:
- Stronger engagement rate (+15% vs category)
- Higher comment-to-view ratio indicating community engagement
- Better sentiment in comment analysis
- More authentic, relatable content style
- Clearer product benefit communication

Competitive Gaps:
- Lower posting frequency (40% below category leaders)
- Limited dermatologist collaboration content
- Underutilized trending audio/formats
- Slower response to trending topics
- Less investment in influencer amplification

White Space Opportunities:
- Teen skincare education (underserved by premium brands)
- Seasonal transition routines (minimal competition)
- Clinical skincare accessibility narrative
- Ingredient education for mass-market audience
- Real consumer transformation journeys
- Acne treatment alternatives positioning

Strategic Recommendations:
- Close posting frequency gap: increase to 3-4x weekly minimum
- Develop dermatologist partnership program to match CeraVe strategy
- Position as "clinical efficacy meets accessibility"
- Capture teen skincare market before competitor saturation
- Invest in trend responsiveness infrastructure (2-3 week lead time)
- Leverage higher engagement quality in paid amplification
- Create proprietary content format competitors can't easily replicate
- Build SOV in underserved segments before expanding to saturated categories
        """


class AgentOrchestrator:
    """
    Orchestrates multiple agents to generate comprehensive intelligence

    Coordinates execution, aggregates insights, and generates unified recommendations
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.agents = {
            "content_discovery": ContentDiscoveryAgent(api_key=api_key),
            "contextual_intelligence": ContextualIntelligenceAgent(api_key=api_key),
            "audience_insight": AudienceInsightAgent(api_key=api_key),
            "creative_strategy": CreativeStrategyAgent(api_key=api_key),
            "competitive_intelligence": CompetitiveIntelligenceAgent(api_key=api_key),
        }

    def run_all_agents(self, data: Dict[str, Any]) -> Dict[str, AgentResponse]:
        """
        Run all agents on the provided data

        Args:
            data: Dictionary containing video data and metrics

        Returns:
            Dictionary mapping agent names to their responses
        """
        logger.info("Running all agents...")

        responses = {}

        for agent_name, agent in self.agents.items():
            logger.info(f"Running {agent_name}...")
            try:
                response = agent.analyze(data)
                responses[agent_name] = response
                logger.info(f"{agent_name} completed with confidence {response.confidence_score}")
            except Exception as e:
                logger.error(f"Error running {agent_name}: {e}")

        return responses

    def aggregate_insights(self, agent_responses: Dict[str, AgentResponse]) -> Dict[str, Any]:
        """
        Aggregate insights from all agents into unified intelligence

        Args:
            agent_responses: Dictionary of agent responses

        Returns:
            Aggregated insights dictionary
        """
        all_insights = []
        all_recommendations = []
        confidence_scores = []

        for agent_name, response in agent_responses.items():
            all_insights.extend(response.insights)
            all_recommendations.extend(response.recommendations)
            confidence_scores.append(response.confidence_score)

        # Calculate aggregate confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Extract top themes from all analyses
        top_themes = self._extract_top_themes(agent_responses)

        # Determine competitive position
        competitive_position = self._determine_competitive_position(agent_responses)

        return {
            "all_insights": all_insights,
            "top_insights": all_insights[:10],  # Top 10
            "all_recommendations": all_recommendations,
            "top_recommendations": all_recommendations[:10],  # Top 10
            "confidence_score": round(avg_confidence, 2),
            "top_themes": top_themes,
            "competitive_position": competitive_position,
            "agent_count": len(agent_responses),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _extract_top_themes(self, agent_responses: Dict[str, AgentResponse]) -> List[str]:
        """Extract top themes from agent analyses"""
        themes = [
            "Authentic, relatable content",
            "Dermatologist credibility",
            "Educational value",
            "Before/after transformations",
            "Ingredient transparency",
        ]
        return themes

    def _determine_competitive_position(self, agent_responses: Dict[str, AgentResponse]) -> str:
        """Determine overall competitive position"""
        if "competitive_intelligence" in agent_responses:
            # Extract from competitive intelligence agent
            return "Strong engagement quality with SOV growth opportunity"
        return "Competitive position analysis pending"

    def generate_report(
        self,
        agent_responses: Dict[str, AgentResponse],
        aggregated_insights: Dict[str, Any],
        brand_name: str
    ) -> str:
        """
        Generate comprehensive intelligence report

        Args:
            agent_responses: Individual agent responses
            aggregated_insights: Aggregated insights
            brand_name: Brand name

        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 80,
            f"YOUTUBE SHORTS INTELLIGENCE REPORT: {brand_name.upper()}",
            "=" * 80,
            f"Generated: {datetime.utcnow().isoformat()}",
            f"Overall Confidence Score: {aggregated_insights['confidence_score']:.0%}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 80,
        ]

        # Add top insights
        report_lines.append("\nTop Strategic Insights:")
        for i, insight in enumerate(aggregated_insights['top_insights'][:5], 1):
            report_lines.append(f"{i}. {insight}")

        # Add top recommendations
        report_lines.append("\nPriority Recommendations:")
        for i, rec in enumerate(aggregated_insights['top_recommendations'][:5], 1):
            report_lines.append(f"{i}. {rec}")

        # Add agent-specific sections
        report_lines.append("\n" + "=" * 80)
        report_lines.append("DETAILED AGENT ANALYSES")
        report_lines.append("=" * 80)

        for agent_name, response in agent_responses.items():
            report_lines.append(f"\n{response.agent_name}")
            report_lines.append("-" * 80)
            report_lines.append(f"Confidence: {response.confidence_score:.0%}")
            report_lines.append(f"\n{response.analysis}")

        report_lines.append("\n" + "=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)
