-- Channel Performance Over Time
-- Use this to create a time-series chart of ROI and ROAS by channel
SELECT
    date_day,
    channel_name,
    roi,
    roas,
    total_spend,
    total_revenue
FROM
    mv_daily_channel_metrics
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
ORDER BY
    date_day, channel_name;

-- Customer Acquisition Cost Analysis
-- Use this to create a bar chart comparing CAC across channels
SELECT
    channel_name,
    AVG(cac) AS avg_cac,
    AVG(avg_clv) AS avg_customer_lifetime_value,
    AVG(clv_cac_ratio) AS avg_clv_to_cac_ratio
FROM
    mv_daily_channel_metrics
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
GROUP BY
    channel_name
ORDER BY
    avg_cac DESC;

-- Funnel Analysis By Channel
-- Use this to create a funnel visualization
SELECT
    channel_name,
    SUM(tofu_events) AS awareness_stage,
    SUM(mofu_events) AS consideration_stage,
    SUM(bofu_events) AS decision_stage,
    SUM(conversion_events) AS conversion_stage,
    AVG(tofu_to_mofu_rate) * 100 AS awareness_to_consideration_rate,
    AVG(mofu_to_bofu_rate) * 100 AS consideration_to_decision_rate,
    AVG(bofu_to_conversion_rate) * 100 AS decision_to_conversion_rate,
    AVG(overall_conversion_rate) * 100 AS overall_conversion_rate
FROM
    mv_funnel_conversion_rates
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
GROUP BY
    channel_name;

-- Budget Utilization and Variance
-- Use this to create a combined bar and line chart
SELECT
    channel_name,
    SUM(planned_budget) AS total_planned_budget,
    SUM(actual_spend) AS total_actual_spend,
    SUM(budget_variance) AS total_budget_variance,
    AVG(budget_utilization_pct) AS avg_budget_utilization
FROM
    mv_budget_vs_actual
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
GROUP BY
    channel_name
ORDER BY
    total_planned_budget DESC;

-- Forecast Accuracy Trend
-- Use this to create a line chart showing forecast accuracy over time
SELECT
    date_day,
    channel_name,
    predicted_roi,
    actual_roi,
    roi_variance,
    forecast_accuracy_pct
FROM
    mv_forecast_accuracy
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
ORDER BY
    date_day, channel_name;

-- Channel ROI Comparison
-- Use this to create a pie chart or bar chart showing ROI distribution
SELECT
    channel_name,
    AVG(roi) AS average_roi,
    SUM(total_revenue - total_spend) AS total_profit
FROM
    mv_daily_channel_metrics
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}
GROUP BY
    channel_name
ORDER BY
    average_roi DESC;

-- Daily KPIs for Marketing Dashboard
-- Use this for summary metrics and KPI tiles
SELECT
    SUM(total_spend) AS total_marketing_spend,
    SUM(total_revenue) AS total_revenue_generated,
    SUM(total_revenue) / NULLIF(SUM(total_spend), 0) AS overall_roas,
    (SUM(total_revenue) - SUM(total_spend)) / NULLIF(SUM(total_spend), 0) AS overall_roi,
    SUM(total_spend) / NULLIF(SUM(converted_users), 0) AS overall_cac
FROM
    mv_daily_channel_metrics
WHERE
    date_day BETWEEN '{{start_date}}' AND '{{end_date}}'
    {% if channel_name %}
    AND channel_name = '{{channel_name}}'
    {% endif %}; 