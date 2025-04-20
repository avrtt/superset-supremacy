-- Drop existing materialized views if they exist
DROP MATERIALIZED VIEW IF EXISTS mv_daily_channel_metrics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_funnel_conversion_rates CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_budget_vs_actual CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_forecast_accuracy CASCADE;

-- Create materialized view for daily channel metrics (ROI, ROAS, CAC, CLV)
CREATE MATERIALIZED VIEW mv_daily_channel_metrics
AS
SELECT
    date_trunc('day', c.campaign_date) AS date_day,
    ch.channel_name,
    ch.channel_id,
    SUM(c.spend) AS total_spend,
    SUM(conv.revenue) AS total_revenue,
    COUNT(DISTINCT conv.user_id) AS converted_users,
    SUM(conv.revenue) / NULLIF(SUM(c.spend), 0) AS roas,
    (SUM(conv.revenue) - SUM(c.spend)) / NULLIF(SUM(c.spend), 0) AS roi,
    SUM(c.spend) / NULLIF(COUNT(DISTINCT conv.user_id), 0) AS cac,
    SUM(conv.customer_lifetime_value) / NULLIF(COUNT(DISTINCT conv.user_id), 0) AS avg_clv,
    SUM(conv.customer_lifetime_value) / NULLIF(SUM(c.spend), 0) AS clv_cac_ratio
FROM
    campaigns c
JOIN
    channels ch ON c.channel_id = ch.channel_id
LEFT JOIN
    conversions conv ON c.campaign_id = conv.campaign_id
GROUP BY
    date_day, ch.channel_name, ch.channel_id
WITH DATA;

-- Create index for better query performance
CREATE INDEX idx_mv_daily_channel_metrics_date_channel
ON mv_daily_channel_metrics (date_day, channel_id);

-- Create materialized view for funnel conversion rates (TOFU, MOFU, BOFU)
CREATE MATERIALIZED VIEW mv_funnel_conversion_rates
AS
SELECT
    date_trunc('day', fe.event_timestamp) AS date_day,
    ch.channel_id,
    ch.channel_name,
    SUM(CASE WHEN fe.event_type = 'page_view' THEN 1 ELSE 0 END) AS tofu_events,
    SUM(CASE WHEN fe.event_type = 'content_engagement' THEN 1 ELSE 0 END) AS mofu_events,
    SUM(CASE WHEN fe.event_type = 'product_view' OR fe.event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS bofu_events,
    SUM(CASE WHEN fe.event_type = 'purchase' THEN 1 ELSE 0 END) AS conversion_events,
    SUM(CASE WHEN fe.event_type = 'content_engagement' THEN 1 ELSE 0 END)::float / 
        NULLIF(SUM(CASE WHEN fe.event_type = 'page_view' THEN 1 ELSE 0 END), 0) AS tofu_to_mofu_rate,
    SUM(CASE WHEN fe.event_type = 'product_view' OR fe.event_type = 'add_to_cart' THEN 1 ELSE 0 END)::float / 
        NULLIF(SUM(CASE WHEN fe.event_type = 'content_engagement' THEN 1 ELSE 0 END), 0) AS mofu_to_bofu_rate,
    SUM(CASE WHEN fe.event_type = 'purchase' THEN 1 ELSE 0 END)::float / 
        NULLIF(SUM(CASE WHEN fe.event_type = 'product_view' OR fe.event_type = 'add_to_cart' THEN 1 ELSE 0 END), 0) AS bofu_to_conversion_rate,
    SUM(CASE WHEN fe.event_type = 'purchase' THEN 1 ELSE 0 END)::float / 
        NULLIF(SUM(CASE WHEN fe.event_type = 'page_view' THEN 1 ELSE 0 END), 0) AS overall_conversion_rate
FROM
    funnel_events fe
JOIN
    campaigns c ON fe.campaign_id = c.campaign_id
JOIN
    channels ch ON c.channel_id = ch.channel_id
GROUP BY
    date_day, ch.channel_id, ch.channel_name
WITH DATA;

-- Create index for better query performance
CREATE INDEX idx_mv_funnel_conversion_rates_date_channel
ON mv_funnel_conversion_rates (date_day, channel_id);

-- Create materialized view for budget vs actual spend analysis
CREATE MATERIALIZED VIEW mv_budget_vs_actual
AS
SELECT
    date_trunc('day', c.campaign_date) AS date_day,
    ch.channel_id,
    ch.channel_name,
    SUM(c.budget) AS planned_budget,
    SUM(c.spend) AS actual_spend,
    SUM(c.spend) - SUM(c.budget) AS budget_variance,
    CASE 
        WHEN SUM(c.budget) > 0 THEN (SUM(c.spend) / SUM(c.budget)) * 100 
        ELSE NULL 
    END AS budget_utilization_pct
FROM
    campaigns c
JOIN
    channels ch ON c.channel_id = ch.channel_id
GROUP BY
    date_day, ch.channel_id, ch.channel_name
WITH DATA;

-- Create index for better query performance
CREATE INDEX idx_mv_budget_vs_actual_date_channel
ON mv_budget_vs_actual (date_day, channel_id);

-- Create materialized view for forecast accuracy analysis
CREATE MATERIALIZED VIEW mv_forecast_accuracy
AS
SELECT
    date_trunc('day', c.campaign_date) AS date_day,
    ch.channel_id,
    ch.channel_name,
    SUM(c.predicted_roi) AS predicted_roi,
    SUM(CASE WHEN conv.revenue > 0 THEN (conv.revenue - c.spend) / c.spend ELSE 0 END) AS actual_roi,
    SUM(c.predicted_roi) - SUM(CASE WHEN conv.revenue > 0 THEN (conv.revenue - c.spend) / c.spend ELSE 0 END) AS roi_variance,
    CASE 
        WHEN SUM(c.predicted_roi) <> 0 THEN 
            (1 - ABS(SUM(c.predicted_roi) - SUM(CASE WHEN conv.revenue > 0 THEN (conv.revenue - c.spend) / c.spend ELSE 0 END)) / ABS(SUM(c.predicted_roi))) * 100
        ELSE NULL
    END AS forecast_accuracy_pct
FROM
    campaigns c
JOIN
    channels ch ON c.channel_id = ch.channel_id
LEFT JOIN
    conversions conv ON c.campaign_id = conv.campaign_id
GROUP BY
    date_day, ch.channel_id, ch.channel_name
WITH DATA;

-- Create index for better query performance
CREATE INDEX idx_mv_forecast_accuracy_date_channel
ON mv_forecast_accuracy (date_day, channel_id);

-- Create refresh function for materialized views
CREATE OR REPLACE FUNCTION refresh_marketing_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_channel_metrics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_funnel_conversion_rates;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_budget_vs_actual;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_forecast_accuracy;
END;
$$ LANGUAGE plpgsql;

-- Comment describing how to schedule refresh
COMMENT ON FUNCTION refresh_marketing_materialized_views() IS 
'Run this function daily to refresh all marketing materialized views.
Example cron job: 
0 1 * * * psql -U username -d database_name -c "SELECT refresh_marketing_materialized_views();"'; 