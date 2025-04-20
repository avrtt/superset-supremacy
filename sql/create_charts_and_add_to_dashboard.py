#!/usr/bin/env python

import json
import requests
import time
import traceback
import sys

# Superset API credentials and URLs
SUPERSET_URL = 'http://localhost:8088'
USERNAME = 'admin'
PASSWORD = 'admin'

# API endpoints
LOGIN_URL = f'{SUPERSET_URL}/api/v1/security/login'
DATASET_URL = f'{SUPERSET_URL}/api/v1/dataset/'
CHART_URL = f'{SUPERSET_URL}/api/v1/chart/'
DASHBOARD_URL = f'{SUPERSET_URL}/api/v1/dashboard/'
DASHBOARD_CHART_URL = f'{SUPERSET_URL}/api/v1/dashboard/'

# The database ID for Marketing Analytics - will be fetched
DATABASE_ID = None
# The dashboard ID - will be fetched by name
DASHBOARD_ID = None
# Dataset IDs
DATASET_IDS = {}

def get_auth_token():
    """Get the auth token from Superset API"""
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'provider': 'db'
    }
    
    try:
        print(f"Attempting to login to {LOGIN_URL}")
        resp = requests.post(LOGIN_URL, json=login_data)
        print(f"Login response status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return None
            
        return resp.json().get('access_token')
    except Exception as e:
        print(f"Error getting auth token: {str(e)}")
        traceback.print_exc()
        return None

def get_headers(token):
    """Create headers with auth token"""
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def get_database_id(token):
    """Get the database ID for Marketing Analytics"""
    global DATABASE_ID
    
    headers = get_headers(token)
    resp = requests.get(f'{SUPERSET_URL}/api/v1/database/', headers=headers)
    
    if resp.status_code != 200:
        print(f"Failed to get database list: {resp.text}")
        return None
    
    databases = resp.json()['result']
    for db in databases:
        if db['database_name'] == 'Marketing Analytics':
            DATABASE_ID = db['id']
            print(f"Found Marketing Analytics database with ID: {DATABASE_ID}")
            return DATABASE_ID
    
    print("Marketing Analytics database not found")
    return None

def get_dashboard_id(token):
    """Get the dashboard ID for Marketing Strategy Dashboard"""
    global DASHBOARD_ID
    
    headers = get_headers(token)
    resp = requests.get(f'{DASHBOARD_URL}', headers=headers)
    
    if resp.status_code != 200:
        print(f"Failed to get dashboard list: {resp.text}")
        return None
    
    dashboards = resp.json()['result']
    for dashboard in dashboards:
        if dashboard['dashboard_title'] == 'Marketing Strategy Dashboard':
            DASHBOARD_ID = dashboard['id']
            print(f"Found Marketing Strategy Dashboard with ID: {DASHBOARD_ID}")
            return DASHBOARD_ID
    
    print("Marketing Strategy Dashboard not found")
    return None

def create_datasets(token):
    """Create datasets for the materialized views"""
    global DATASET_IDS
    
    headers = get_headers(token)
    
    # Define datasets to create
    dataset_configs = [
        {
            'name': 'mv_daily_channel_metrics',
            'table_name': 'mv_daily_channel_metrics'
        },
        {
            'name': 'mv_funnel_conversion_rates',
            'table_name': 'mv_funnel_conversion_rates'
        },
        {
            'name': 'mv_budget_vs_actual',
            'table_name': 'mv_budget_vs_actual'
        },
        {
            'name': 'mv_forecast_accuracy',
            'table_name': 'mv_forecast_accuracy'
        }
    ]
    
    # Check if datasets already exist
    resp = requests.get(DATASET_URL, headers=headers)
    existing_datasets = resp.json()['result']
    existing_dataset_names = [d['table_name'] for d in existing_datasets]
    
    for config in dataset_configs:
        if config['table_name'] in existing_dataset_names:
            # Get existing dataset ID
            for d in existing_datasets:
                if d['table_name'] == config['table_name']:
                    DATASET_IDS[config['name']] = d['id']
                    print(f"Dataset {config['name']} already exists with ID: {DATASET_IDS[config['name']]}")
        else:
            # Create new dataset
            dataset_data = {
                'database': DATABASE_ID,
                'schema': 'public',
                'table_name': config['table_name']
            }
            
            resp = requests.post(DATASET_URL, headers=headers, json=dataset_data)
            
            if resp.status_code == 201:
                dataset_id = resp.json()['id']
                DATASET_IDS[config['name']] = dataset_id
                print(f"Created dataset {config['name']} with ID: {dataset_id}")
            else:
                print(f"Failed to create dataset {config['name']}: {resp.text}")
    
    return len(DATASET_IDS) == len(dataset_configs)

def create_chart(token, chart_config):
    """Create a chart in Superset"""
    headers = get_headers(token)
    
    resp = requests.post(CHART_URL, headers=headers, json=chart_config)
    
    if resp.status_code == 201:
        chart_id = resp.json()['id']
        print(f"Created chart {chart_config['slice_name']} with ID: {chart_id}")
        return chart_id
    else:
        print(f"Failed to create chart {chart_config['slice_name']}: {resp.status_code} - {resp.text}")
        return None

def add_chart_to_dashboard(token, dashboard_id, chart_id, position):
    """Add a chart to the dashboard"""
    headers = get_headers(token)
    
    # First, get the current dashboard layout
    resp = requests.get(f'{DASHBOARD_URL}{dashboard_id}', headers=headers)
    if resp.status_code != 200:
        print(f"Failed to get dashboard details: {resp.text}")
        return False
    
    dashboard_data = resp.json()['result']
    position_json = json.loads(dashboard_data['position_json'])
    
    # Add the chart to the specified position in the layout
    chart_component = {
        "type": "CHART",
        "id": f"CHART-{chart_id}",
        "children": [],
        "parents": ["ROOT_ID", "GRID_ID"],
        "meta": {
            "width": position['width'],
            "height": position['height'],
            "chartId": chart_id,
            "sliceName": position['slice_name']
        }
    }
    
    # Add chart to the grid layout
    grid = position_json.get("GRID_ID", {})
    children = grid.get("children", [])
    children.append(f"CHART-{chart_id}")
    grid["children"] = children
    position_json["GRID_ID"] = grid
    
    # Add the chart component to the position JSON
    position_json[f"CHART-{chart_id}"] = chart_component
    
    # Update the dashboard with the new layout
    update_data = {
        "json_metadata": dashboard_data['json_metadata'],
        "position_json": json.dumps(position_json)
    }
    
    resp = requests.put(f'{DASHBOARD_URL}{dashboard_id}', headers=headers, json=update_data)
    if resp.status_code == 200:
        print(f"Added chart {position['slice_name']} to dashboard")
        return True
    else:
        print(f"Failed to update dashboard layout: {resp.text}")
        return False

def create_dashboard_charts(token):
    """Create all charts and add them to the dashboard"""
    # Define all chart configurations to create
    chart_configs = [
        # KPI Metrics
        {
            "slice_name": "Total Marketing Spend",
            "viz_type": "big_number_total",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "date_format": "smart_date",
                "granularity_sqla": "date_day",
                "header_font_size": 15,
                "metric": {
                    "aggregate": "SUM",
                    "column": {"column_name": "total_spend"},
                    "expressionType": "SIMPLE",
                    "label": "Total Spend"
                },
                "subheader_font_size": 12,
                "time_range": "Last 90 days",
                "viz_type": "big_number_total",
                "y_axis_format": "$,.2f"
            }),
            "position": {
                "width": 3,
                "height": 6,
                "slice_name": "Total Marketing Spend"
            }
        },
        {
            "slice_name": "Overall ROAS",
            "viz_type": "big_number_total",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "date_format": "smart_date",
                "granularity_sqla": "date_day",
                "header_font_size": 15,
                "metric": {
                    "aggregate": "AVG",
                    "column": {"column_name": "roas"},
                    "expressionType": "SIMPLE",
                    "label": "Avg ROAS"
                },
                "subheader_font_size": 12,
                "time_range": "Last 90 days",
                "viz_type": "big_number_total",
                "y_axis_format": ",.2f"
            }),
            "position": {
                "width": 3,
                "height": 6,
                "slice_name": "Overall ROAS"
            }
        },
        {
            "slice_name": "Overall ROI",
            "viz_type": "big_number_total",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "date_format": "smart_date",
                "granularity_sqla": "date_day",
                "header_font_size": 15,
                "metric": {
                    "aggregate": "AVG",
                    "column": {"column_name": "roi"},
                    "expressionType": "SIMPLE",
                    "label": "Avg ROI"
                },
                "subheader_font_size": 12,
                "time_range": "Last 90 days",
                "viz_type": "big_number_total",
                "y_axis_format": ",.1%"
            }),
            "position": {
                "width": 3,
                "height": 6,
                "slice_name": "Overall ROI"
            }
        },
        {
            "slice_name": "Average CAC",
            "viz_type": "big_number_total",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "date_format": "smart_date",
                "granularity_sqla": "date_day",
                "header_font_size": 15,
                "metric": {
                    "aggregate": "AVG",
                    "column": {"column_name": "cac"},
                    "expressionType": "SIMPLE",
                    "label": "Avg CAC"
                },
                "subheader_font_size": 12,
                "time_range": "Last 90 days",
                "viz_type": "big_number_total",
                "y_axis_format": "$,.2f"
            }),
            "position": {
                "width": 3,
                "height": 6,
                "slice_name": "Average CAC"
            }
        },
        # Channel Performance
        {
            "slice_name": "ROI Trend by Channel",
            "viz_type": "line",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "line_interpolation": "basis",
                "metrics": [{
                    "aggregate": "AVG",
                    "column": {"column_name": "roi"},
                    "expressionType": "SIMPLE",
                    "label": "ROI"
                }],
                "rich_tooltip": True,
                "row_limit": 10000,
                "show_legend": True,
                "time_range": "Last 90 days",
                "viz_type": "line",
                "x_axis_format": "smart_date",
                "y_axis_format": ",.1%"
            }),
            "position": {
                "width": 12,
                "height": 10,
                "slice_name": "ROI Trend by Channel"
            }
        },
        {
            "slice_name": "Channel ROI Comparison",
            "viz_type": "pie",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metric": {
                    "aggregate": "AVG",
                    "column": {"column_name": "roi"},
                    "expressionType": "SIMPLE",
                    "label": "Avg ROI"
                },
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "pie",
                "donut": True,
                "labels_outside": True,
                "show_legend": True,
                "show_labels": True,
                "label_type": "key_percent"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Channel ROI Comparison"
            }
        },
        {
            "slice_name": "CAC by Channel",
            "viz_type": "dist_bar",
            "datasource_id": DATASET_IDS['mv_daily_channel_metrics'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "bottom_margin": "auto",
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_daily_channel_metrics']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [{
                    "aggregate": "AVG",
                    "column": {"column_name": "cac"},
                    "expressionType": "SIMPLE",
                    "label": "Avg CAC"
                }],
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "dist_bar",
                "x_axis_label": "Channel",
                "y_axis_format": "$,.2f",
                "y_axis_label": "Customer Acquisition Cost"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "CAC by Channel"
            }
        },
        # Funnel Analysis
        {
            "slice_name": "Marketing Funnel",
            "viz_type": "funnel",
            "datasource_id": DATASET_IDS['mv_funnel_conversion_rates'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_funnel_conversion_rates']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "tofu_events"},
                        "expressionType": "SIMPLE",
                        "label": "Awareness"
                    },
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "mofu_events"},
                        "expressionType": "SIMPLE",
                        "label": "Consideration"
                    },
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "bofu_events"},
                        "expressionType": "SIMPLE",
                        "label": "Decision"
                    },
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "conversion_events"},
                        "expressionType": "SIMPLE",
                        "label": "Conversion"
                    }
                ],
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "funnel",
                "sort_by_metric": True
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Marketing Funnel"
            }
        },
        {
            "slice_name": "Conversion Rates by Channel",
            "viz_type": "dist_bar",
            "datasource_id": DATASET_IDS['mv_funnel_conversion_rates'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "bottom_margin": "auto",
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_funnel_conversion_rates']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "tofu_to_mofu_rate"},
                        "expressionType": "SIMPLE",
                        "label": "Awareness → Consideration"
                    },
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "mofu_to_bofu_rate"},
                        "expressionType": "SIMPLE",
                        "label": "Consideration → Decision"
                    },
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "bofu_to_conversion_rate"},
                        "expressionType": "SIMPLE",
                        "label": "Decision → Purchase"
                    },
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "overall_conversion_rate"},
                        "expressionType": "SIMPLE",
                        "label": "Overall Conversion"
                    }
                ],
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "dist_bar",
                "x_axis_label": "Channel",
                "y_axis_format": ",.1%",
                "y_axis_label": "Conversion Rate"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Conversion Rates by Channel"
            }
        },
        # Budget Analysis 
        {
            "slice_name": "Budget vs Actual Spend",
            "viz_type": "dist_bar",
            "datasource_id": DATASET_IDS['mv_budget_vs_actual'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "bottom_margin": "auto",
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_budget_vs_actual']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "planned_budget"},
                        "expressionType": "SIMPLE",
                        "label": "Planned Budget"
                    },
                    {
                        "aggregate": "SUM",
                        "column": {"column_name": "actual_spend"},
                        "expressionType": "SIMPLE",
                        "label": "Actual Spend"
                    }
                ],
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "dist_bar",
                "x_axis_label": "Channel",
                "y_axis_format": "$,.0f",
                "y_axis_label": "Budget"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Budget vs Actual Spend"
            }
        },
        {
            "slice_name": "Budget Utilization",
            "viz_type": "dist_bar",
            "datasource_id": DATASET_IDS['mv_budget_vs_actual'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "bottom_margin": "auto",
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_budget_vs_actual']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [{
                    "aggregate": "AVG",
                    "column": {"column_name": "budget_utilization_pct"},
                    "expressionType": "SIMPLE",
                    "label": "Budget Utilization %"
                }],
                "row_limit": 10,
                "time_range": "Last 90 days",
                "viz_type": "dist_bar",
                "x_axis_label": "Channel",
                "y_axis_format": ",.1%",
                "y_axis_label": "Utilization Percentage"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Budget Utilization"
            }
        },
        # ROI Forecasting
        {
            "slice_name": "Forecast Accuracy",
            "viz_type": "big_number_total",
            "datasource_id": DATASET_IDS['mv_forecast_accuracy'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "datasource": f"{DATASET_IDS['mv_forecast_accuracy']}__table",
                "date_format": "smart_date",
                "granularity_sqla": "date_day",
                "header_font_size": 15,
                "metric": {
                    "aggregate": "AVG",
                    "column": {"column_name": "forecast_accuracy_pct"},
                    "expressionType": "SIMPLE",
                    "label": "Forecast Accuracy"
                },
                "subheader_font_size": 12,
                "time_range": "Last 90 days",
                "viz_type": "big_number_total",
                "y_axis_format": ",.1%"
            }),
            "position": {
                "width": 6,
                "height": 6,
                "slice_name": "Forecast Accuracy"
            }
        },
        {
            "slice_name": "Predicted vs Actual ROI",
            "viz_type": "line",
            "datasource_id": DATASET_IDS['mv_forecast_accuracy'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_forecast_accuracy']}__table",
                "granularity_sqla": "date_day",
                "metrics": [
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "predicted_roi"},
                        "expressionType": "SIMPLE",
                        "label": "Predicted ROI"
                    },
                    {
                        "aggregate": "AVG",
                        "column": {"column_name": "actual_roi"},
                        "expressionType": "SIMPLE",
                        "label": "Actual ROI"
                    }
                ],
                "rich_tooltip": True,
                "row_limit": 10000,
                "show_legend": True,
                "time_range": "Last 90 days",
                "viz_type": "line",
                "x_axis_format": "smart_date",
                "y_axis_format": ",.1%"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Predicted vs Actual ROI"
            }
        },
        {
            "slice_name": "Forecast Accuracy Trend",
            "viz_type": "line",
            "datasource_id": DATASET_IDS['mv_forecast_accuracy'],
            "datasource_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "datasource": f"{DATASET_IDS['mv_forecast_accuracy']}__table",
                "granularity_sqla": "date_day",
                "groupby": ["channel_name"],
                "metrics": [{
                    "aggregate": "AVG",
                    "column": {"column_name": "forecast_accuracy_pct"},
                    "expressionType": "SIMPLE",
                    "label": "Forecast Accuracy"
                }],
                "rich_tooltip": True,
                "row_limit": 10000,
                "show_legend": True,
                "time_range": "Last 90 days",
                "viz_type": "line",
                "x_axis_format": "smart_date",
                "y_axis_format": ",.1%"
            }),
            "position": {
                "width": 6,
                "height": 10,
                "slice_name": "Forecast Accuracy Trend"
            }
        }
    ]
    
    # Create each chart and add to dashboard
    success_count = 0
    for config in chart_configs:
        chart_id = create_chart(token, {
            "slice_name": config["slice_name"],
            "viz_type": config["viz_type"],
            "datasource_id": config["datasource_id"],
            "datasource_type": config["datasource_type"],
            "params": config["params"]
        })
        
        if chart_id:
            success = add_chart_to_dashboard(token, DASHBOARD_ID, chart_id, config["position"])
            if success:
                success_count += 1
            time.sleep(1)  # Brief delay to avoid overwhelming the API
    
    return success_count == len(chart_configs)

def main():
    """Main execution flow"""
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token. Exiting.")
        sys.exit(1)
    
    # Get database ID
    if not get_database_id(token):
        print("Failed to get database ID. Exiting.")
        sys.exit(1)
    
    # Get dashboard ID
    if not get_dashboard_id(token):
        print("Failed to get dashboard ID. Exiting.")
        sys.exit(1)
    
    # Create datasets
    if not create_datasets(token):
        print("Failed to create all required datasets. Some charts may not render correctly.")
    
    # Create charts and add to dashboard
    success = create_dashboard_charts(token)
    
    if success:
        print("\n✅ Successfully created all charts and added them to the dashboard!")
        print(f"Access your dashboard at: {SUPERSET_URL}/superset/dashboard/{DASHBOARD_ID}/")
    else:
        print("\n⚠️ Some charts could not be created or added to the dashboard.")
        print("Check the logs above for more details.")
    
if __name__ == "__main__":
    main() 