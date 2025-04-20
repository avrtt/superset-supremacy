#!/usr/bin/env python

import json
import os
import sys
import time
import traceback
from sqlalchemy import create_engine
import requests

# Superset API credentials and URLs
SUPERSET_URL = 'http://localhost:8088'
USERNAME = 'admin'
PASSWORD = 'admin'

# API endpoints
LOGIN_URL = f'{SUPERSET_URL}/api/v1/security/login'
CHARTS_URL = f'{SUPERSET_URL}/api/v1/chart/'
DASHBOARD_URL = f'{SUPERSET_URL}/api/v1/dashboard/'

def get_auth_token():
    """Get the auth token from Superset API"""
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'provider': 'db',  # Using the DB authentication provider
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

def create_marketing_dashboard():
    """Create the marketing dashboard in Superset"""
    print("Creating Marketing Strategy Dashboard...")
    
    # Wait for Superset to be fully initialized
    print("Waiting for Superset API to be ready...")
    max_retries = 10
    retries = 0
    
    while retries < max_retries:
        try:
            resp = requests.get(f'{SUPERSET_URL}/health')
            if resp.status_code == 200:
                print("Superset is ready!")
                break
        except:
            pass
            
        retries += 1
        print(f"Waiting for Superset API (attempt {retries}/{max_retries})...")
        time.sleep(5)
    
    if retries >= max_retries:
        print("Superset API did not become available in time.")
        print("You may need to manually create the dashboard once Superset is fully initialized.")
        print("1. Log in to Superset at http://localhost:8088")
        print("2. Go to Dashboards -> + Dashboard")
        print("3. Name it 'Marketing Strategy Dashboard'")
        print("4. Create datasets for the materialized views and add charts to the dashboard")
        return None
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Cannot create dashboard automatically.")
        return None
        
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    # Create dashboard
    dashboard_data = {
        "dashboard_title": "Marketing Strategy Dashboard",
        "published": True,
        "json_metadata": json.dumps({
            "filter_scopes": {},
            "timed_refresh_immune_slices": [],
            "expanded_slices": {},
            "refresh_frequency": 3600,
            "color_scheme": "darkBlue",
            "label_colors": {
                "Facebook": "#1F77B4",
                "Google": "#2CA02C",
                "Instagram": "#9467BD",
                "LinkedIn": "#FF7F0E",
                "TikTok": "#D62728",
                "Twitter": "#8C564B",
                "YouTube": "#E377C2"
            },
            "shared_label_colors": {
                "Paid Search": "#2196f3",
                "Social Media": "#4caf50",
                "Email": "#ff9800",
                "Display": "#9c27b0",
                "Affiliate": "#e91e63",
                "Referral": "#607d8b"
            }
        }),
        "owners": [1],  # Assuming admin user has id 1
        "position_json": json.dumps({
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
            "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]}
        })
    }
    
    try:
        print(f"Creating dashboard via API: {DASHBOARD_URL}")
        resp = requests.post(DASHBOARD_URL, headers=headers, json=dashboard_data)
        print(f"Dashboard creation response: {resp.status_code}")
        
        if resp.status_code >= 400:
            print(f"Error creating dashboard: {resp.text}")
            return None
            
        dashboard_id = resp.json().get('id')
        
        if dashboard_id:
            print(f"Created dashboard with ID: {dashboard_id}")
            print(f"Access your dashboard at: {SUPERSET_URL}/superset/dashboard/{dashboard_id}/")
            return dashboard_id
        else:
            print("Dashboard ID not found in response.")
            return None
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    dashboard_id = create_marketing_dashboard()
    
    if dashboard_id:
        print("Marketing dashboard created successfully.")
    
    print("To complete dashboard setup:")
    print("1. Log in to Superset at http://localhost:8088")
    print("2. Navigate to Data -> Datasets")
    print("3. Create datasets for the materialized views: mv_daily_channel_metrics, mv_funnel_conversion_rates, mv_budget_vs_actual, mv_forecast_accuracy")
    print("4. Create charts using the examples in sql/marketing_analysis_examples.sql")
    print("5. Add charts to the dashboard") 