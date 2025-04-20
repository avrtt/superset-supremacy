-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS channels (
    channel_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) NOT NULL,
    channel_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    channel_id INTEGER REFERENCES channels(channel_id),
    campaign_date DATE NOT NULL,
    budget DECIMAL(12,2) NOT NULL DEFAULT 0,
    spend DECIMAL(12,2) NOT NULL DEFAULT 0,
    predicted_roi DECIMAL(8,4),
    campaign_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversions (
    conversion_id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    user_id VARCHAR(50) NOT NULL,
    conversion_date TIMESTAMP NOT NULL,
    revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    customer_lifetime_value DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS funnel_events (
    event_id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    user_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for channels
INSERT INTO channels (channel_name, channel_type)
VALUES
    ('Facebook', 'Social Media'),
    ('Google', 'Search'),
    ('Instagram', 'Social Media'),
    ('LinkedIn', 'Social Media'),
    ('Email', 'Direct'),
    ('Twitter', 'Social Media'),
    ('TikTok', 'Social Media'),
    ('YouTube', 'Video')
ON CONFLICT (channel_id) DO NOTHING;

-- Set up date range for sample data
WITH date_range AS (
    SELECT generate_series(
        current_date - interval '90 days', 
        current_date, 
        interval '1 day'
    )::date AS campaign_date
)

-- Insert sample campaigns data
INSERT INTO campaigns (campaign_name, channel_id, campaign_date, budget, spend, predicted_roi, campaign_status)
SELECT 
    'Campaign ' || c.channel_id || '-' || to_char(d.campaign_date, 'YYYYMMDD') AS campaign_name,
    c.channel_id,
    d.campaign_date,
    -- Random budget between 1000 and 5000
    (random() * 4000 + 1000)::numeric(12,2) AS budget,
    -- Random spend between 80% and 120% of budget
    (random() * 0.4 + 0.8) * (random() * 4000 + 1000)::numeric(12,2) AS spend,
    -- Random predicted ROI between 0.5 and 3.0
    (random() * 2.5 + 0.5)::numeric(8,4) AS predicted_roi,
    'active' AS campaign_status
FROM 
    channels c
CROSS JOIN 
    date_range d
WHERE 
    NOT EXISTS (
        SELECT 1 FROM campaigns 
        WHERE channel_id = c.channel_id 
        AND campaign_date = d.campaign_date
    )
ORDER BY 
    c.channel_id, d.campaign_date;

-- Insert sample conversions data
-- For each campaign, randomly create between 5 and 50 conversions
WITH campaign_counts AS (
    SELECT 
        campaign_id,
        channel_id,
        campaign_date,
        spend,
        -- Random number of conversions per campaign
        floor(random() * 45 + 5)::int AS num_conversions
    FROM 
        campaigns
)
INSERT INTO conversions (campaign_id, user_id, conversion_date, revenue, customer_lifetime_value)
SELECT
    cc.campaign_id,
    'user_' || floor(random() * 1000000)::int AS user_id,
    cc.campaign_date + (random() * interval '23 hours 59 minutes')::interval AS conversion_date,
    -- Random revenue between $10 and $500
    (random() * 490 + 10)::numeric(12,2) AS revenue,
    -- Random CLV between $50 and $2000
    (random() * 1950 + 50)::numeric(12,2) AS customer_lifetime_value
FROM
    campaign_counts cc
CROSS JOIN
    generate_series(1, 50) AS s(i)
WHERE
    s.i <= cc.num_conversions
    AND NOT EXISTS (
        SELECT 1 FROM conversions 
        WHERE campaign_id = cc.campaign_id 
        AND user_id = 'user_' || floor(random() * 1000000)::int
    );

-- Insert sample funnel events
-- For each campaign and day, create funnel events
WITH campaign_event_counts AS (
    SELECT 
        campaign_id,
        channel_id,
        campaign_date,
        -- Random number of page views (TOFU events)
        floor(random() * 950 + 50)::int AS num_tofu_events,
        -- Random number of content engagement (MOFU events) - 20-60% of TOFU
        floor(random() * 950 + 50)::int * (random() * 0.4 + 0.2)::int AS num_mofu_events,
        -- Random number of product views/carts (BOFU events) - 10-40% of MOFU
        floor(random() * 950 + 50)::int * (random() * 0.4 + 0.2)::int * (random() * 0.3 + 0.1)::int AS num_bofu_events,
        -- Conversion count from the conversions table
        0 AS num_conversion_events
    FROM 
        campaigns
)
INSERT INTO funnel_events (campaign_id, user_id, event_type, event_timestamp)
SELECT
    cec.campaign_id,
    'user_' || floor(random() * 1000000)::int AS user_id,
    CASE 
        WHEN event_order <= cec.num_tofu_events THEN 'page_view'
        WHEN event_order <= cec.num_tofu_events + cec.num_mofu_events THEN 'content_engagement'
        WHEN event_order <= cec.num_tofu_events + cec.num_mofu_events + cec.num_bofu_events THEN 
            CASE WHEN random() > 0.5 THEN 'product_view' ELSE 'add_to_cart' END
        ELSE 'purchase'
    END AS event_type,
    cec.campaign_date + (random() * interval '23 hours 59 minutes')::interval AS event_timestamp
FROM
    campaign_event_counts cec
CROSS JOIN
    generate_series(1, 2000) AS s(event_order)
WHERE
    event_order <= cec.num_tofu_events + cec.num_mofu_events + cec.num_bofu_events + cec.num_conversion_events
LIMIT 100000; -- Limit to prevent overwhelming the database

-- Insert additional 'purchase' event types based on the conversions table
INSERT INTO funnel_events (campaign_id, user_id, event_type, event_timestamp)
SELECT
    c.campaign_id,
    c.user_id,
    'purchase' AS event_type,
    c.conversion_date AS event_timestamp
FROM
    conversions c
WHERE NOT EXISTS (
    SELECT 1 FROM funnel_events 
    WHERE campaign_id = c.campaign_id 
    AND user_id = c.user_id 
    AND event_type = 'purchase'
); 