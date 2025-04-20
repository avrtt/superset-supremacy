#!/usr/bin/env python

import os
import requests
import json

# Superset API credentials
SUPERSET_URL = 'http://localhost:8088'
USERNAME = 'admin'
PASSWORD = 'admin'

# API endpoints
LOGIN_URL = f'{SUPERSET_URL}/api/v1/security/login'
DASHBOARD_EXPORT_URL = f'{SUPERSET_URL}/api/v1/dashboard/export/'

def get_auth_token():
    """Get authentication token from Superset"""
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'provider': 'db'
    }
    
    resp = requests.post(LOGIN_URL, json=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return None
    
    return resp.json().get('access_token')

def get_dashboard_id():
    """Get the Marketing Strategy Dashboard ID"""
    token = get_auth_token()
    if not token:
        return None
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    resp = requests.get(f'{SUPERSET_URL}/api/v1/dashboard/', headers=headers)
    dashboards = resp.json()['result']
    
    for dashboard in dashboards:
        if dashboard['dashboard_title'] == 'Marketing Strategy Dashboard':
            return dashboard['id']
    
    return None

def export_dashboard(dashboard_id):
    """Export the dashboard with all its charts and datasets"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Dashboard export endpoint requires dashboard ID
    export_url = f'{DASHBOARD_EXPORT_URL}?q={json.dumps({"ids": [dashboard_id]})}'
    resp = requests.get(export_url, headers=headers)
    
    if resp.status_code != 200:
        print(f"Export failed: {resp.text}")
        return False
    
    # Save the exported JSON to assets/complete_dashboard.json
    os.makedirs('assets', exist_ok=True)
    with open('assets/complete_dashboard.json', 'wb') as f:
        f.write(resp.content)
    
    print(f"Dashboard exported successfully to assets/complete_dashboard.json")
    return True

def main():
    print("Exporting Marketing Strategy Dashboard...")
    dashboard_id = get_dashboard_id()
    
    if not dashboard_id:
        print("Dashboard not found. Make sure it's created and properly named.")
        return
    
    if export_dashboard(dashboard_id):
        print("Export complete. The dashboard export includes:")
        print("- The dashboard configuration")
        print("- All charts used in the dashboard")
        print("- Dataset definitions used by the charts")
        print("\nThis file can now be imported during container startup")
    else:
        print("Export failed. Check the logs above.")

if __name__ == "__main__":
    main() 