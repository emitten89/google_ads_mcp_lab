
-- Sentiment analysis by channel
SELECT
    channel_title,
    COUNT(*) as video_count,
    AVG(sentiment_score) as avg_sentiment,
    AVG(engagement_rate) as avg_engagement,
    SUM(view_count) as total_views
FROM default.youtube_shorts.sentiment_scores_10252025
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
FROM default.youtube_shorts.sentiment_scores_10252025
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
FROM default.youtube_shorts.sentiment_scores_10252025
GROUP BY sentiment_category
ORDER BY sentiment_score DESC;

-- Trending vs non-trending performance
SELECT
    is_trending,
    COUNT(*) as video_count,
    AVG(view_count) as avg_views,
    AVG(engagement_rate) as avg_engagement,
    AVG(sentiment_score) as avg_sentiment
FROM default.youtube_shorts.sentiment_scores_10252025
GROUP BY is_trending;
