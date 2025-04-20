This guide will walk you through creating datasets and charts for the **demo** dashboard.

## 1. Create Datasets

First, ensure your dashboard is created but empty. Then follow these steps to create the necessary datasets:

1. Log in to Superset at http://localhost:8088 (credentials: admin/admin)
2. Go to **Data → Datasets**
3. Click **+ Dataset**
4. Select **Marketing Analytics** database
5. Select **public** schema
6. Create the following datasets one by one:
   - **mv_daily_channel_metrics**
   - **mv_funnel_conversion_rates**
   - **mv_budget_vs_actual**
   - **mv_forecast_accuracy**

## 2. Create KPI Charts

Now, let's create the KPI metrics for the top of the dashboard:

### Total Marketing Spend
1. Go to **Charts**
2. Click **+ Chart**
3. Select the **mv_daily_channel_metrics** dataset
4. Choose **Big Number Total** visualization type
5. Configure:
   - Time Column: `date_day`
   - Metric: `SUM(total_spend)`
   - Format Number: `$,.2f`
   - Time Range: `Last 90 days`
6. Run query and save as "Total Marketing Spend"

### Overall ROAS
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Big Number Total** visualization type
4. Configure:
   - Time Column: `date_day`
   - Metric: `AVG(roas)`
   - Format Number: `,.2f`
   - Time Range: `Last 90 days`
5. Run query and save as "Overall ROAS"

### Overall ROI
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Big Number Total** visualization type
4. Configure:
   - Time Column: `date_day`
   - Metric: `AVG(roi)`
   - Format Number: `,.1%`
   - Time Range: `Last 90 days`
5. Run query and save as "Overall ROI"

### Average CAC
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Big Number Total** visualization type
4. Configure:
   - Time Column: `date_day`
   - Metric: `AVG(cac)`
   - Format Number: `$,.2f`
   - Time Range: `Last 90 days`
5. Run query and save as "Average CAC"

### Forecast Accuracy
1. Create a new chart
2. Select the **mv_forecast_accuracy** dataset
3. Choose **Big Number Total** visualization type
4. Configure:
   - Time Column: `date_day`
   - Metric: `AVG(forecast_accuracy_pct)`
   - Format Number: `,.1%`
   - Time Range: `Last 90 days`
5. Run query and save as "Forecast Accuracy"

## 3. Create Channel Performance Charts

### ROI Trend by Channel
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Line Chart** visualization type
4. Configure:
   - Time Column: `date_day`
   - Dimension: `channel_name`
   - Metric: `AVG(roi)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `,.1%`
5. Run query and save as "ROI Trend by Channel"

### Channel ROI Comparison
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Pie Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metric: `AVG(roi)`
   - Time Range: `Last 90 days`
   - Enable "Donut" option
   - Enable "Labels Outside" option
   - Set Label Type to "Key percent"
5. Run query and save as "Channel ROI Comparison"

### CAC by Channel
1. Create a new chart
2. Select the **mv_daily_channel_metrics** dataset
3. Choose **Bar Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metric: `AVG(cac)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `$,.2f`
   - X-Axis Label: "Channel"
   - Y-Axis Label: "Customer Acquisition Cost"
5. Run query and save as "CAC by Channel"

## 4. Create Funnel Analysis Charts

### Marketing Funnel
1. Create a new chart
2. Select the **mv_funnel_conversion_rates** dataset
3. Choose **Funnel Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metrics (in this order):
     - `SUM(tofu_events)` (Rename to "Awareness")
     - `SUM(mofu_events)` (Rename to "Consideration")
     - `SUM(bofu_events)` (Rename to "Decision")
     - `SUM(conversion_events)` (Rename to "Conversion")
   - Time Range: `Last 90 days`
5. Run query and save as "Marketing Funnel"

### Conversion Rates by Channel
1. Create a new chart
2. Select the **mv_funnel_conversion_rates** dataset
3. Choose **Bar Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metrics:
     - `AVG(tofu_to_mofu_rate)` (Rename to "Awareness → Consideration")
     - `AVG(mofu_to_bofu_rate)` (Rename to "Consideration → Decision")
     - `AVG(bofu_to_conversion_rate)` (Rename to "Decision → Purchase")
     - `AVG(overall_conversion_rate)` (Rename to "Overall Conversion")
   - Time Range: `Last 90 days`
   - Y-Axis Format: `,.1%`
   - X-Axis Label: "Channel"
   - Y-Axis Label: "Conversion Rate"
5. Run query and save as "Conversion Rates by Channel"

## 5. Create Budget Analysis Charts

### Budget vs Actual Spend
1. Create a new chart
2. Select the **mv_budget_vs_actual** dataset
3. Choose **Bar Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metrics:
     - `SUM(planned_budget)`
     - `SUM(actual_spend)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `$,.0f`
   - X-Axis Label: "Channel"
   - Y-Axis Label: "Budget"
5. Run query and save as "Budget vs Actual Spend"

### Budget Utilization
1. Create a new chart
2. Select the **mv_budget_vs_actual** dataset
3. Choose **Bar Chart** visualization type
4. Configure:
   - Dimension: `channel_name`
   - Metric: `AVG(budget_utilization_pct)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `,.1%`
   - X-Axis Label: "Channel"
   - Y-Axis Label: "Utilization Percentage"
5. Run query and save as "Budget Utilization"

## 6. Create ROI Forecasting Charts

### Predicted vs Actual ROI
1. Create a new chart
2. Select the **mv_forecast_accuracy** dataset
3. Choose **Line Chart** visualization type
4. Configure:
   - Time Column: `date_day`
   - Metrics:
     - `AVG(predicted_roi)`
     - `AVG(actual_roi)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `,.1%`
5. Run query and save as "Predicted vs Actual ROI"

### Forecast Accuracy Trend
1. Create a new chart
2. Select the **mv_forecast_accuracy** dataset
3. Choose **Line Chart** visualization type
4. Configure:
   - Time Column: `date_day`
   - Dimension: `channel_name`
   - Metric: `AVG(forecast_accuracy_pct)`
   - Time Range: `Last 90 days`
   - Y-Axis Format: `,.1%`
5. Run query and save as "Forecast Accuracy Trend"

## 7. Add Charts to Dashboard

1. Go to **Dashboards**
2. Select your **Marketing Strategy Dashboard**
3. Click **Edit Dashboard**
4. Click **Add charts** from the top 
5. Add all the charts you created
6. Arrange them in the following order:
   - Top row: KPI metrics (Total Marketing Spend, Overall ROAS, Overall ROI, Average CAC, Forecast Accuracy)
   - Second row: ROI Trend by Channel
   - Create tabs for organizing the remaining charts:
     - Tab 1 "Channel Performance": Channel ROI Comparison, CAC by Channel
     - Tab 2 "Funnel Analysis": Marketing Funnel, Conversion Rates by Channel
     - Tab 3 "Budget Analysis": Budget vs Actual Spend, Budget Utilization
     - Tab 4 "ROI Forecasting": Predicted vs Actual ROI, Forecast Accuracy Trend
7. Save the dashboard

## 8. Add Filters (Optional)

1. While in edit mode, click **Add filter**
2. Add the following filters:
   - Date Range filter (connected to all charts)
   - Channel filter (connected to all charts)
3. Save the dashboard

Your Marketing Strategy Dashboard should now be complete with all charts and visualizations! 