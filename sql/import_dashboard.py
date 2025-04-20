#!/usr/bin/env python

import requests
import json
import time
import os

# Superset API credentials
SUPERSET_URL = 'http://localhost:8088'
USERNAME = 'admin'
PASSWORD = 'admin'

# API endpoints
LOGIN_URL = f'{SUPERSET_URL}/api/v1/security/login'
IMPORT_URL = f'{SUPERSET_URL}/api/v1/dashboard/import/'

def get_auth_token():
    """Get authentication token from Superset"""
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'provider': 'db'
    }
    
    # Retry login a few times in case Superset is still starting up
    for attempt in range(5):
        try:
            resp = requests.post(LOGIN_URL, json=login_data)
            if resp.status_code == 200:
                return resp.json().get('access_token')
            print(f"Login attempt {attempt+1} failed. Retrying in 5 seconds...")
            time.sleep(5)
        except requests.exceptions.RequestException:
            print(f"Connection error on attempt {attempt+1}. Retrying in 5 seconds...")
            time.sleep(5)
    
    print("All login attempts failed")
    return None

def import_dashboard():
    """Import the dashboard from the export file"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Check if export file exists
    export_path = '/app/assets/complete_dashboard.json'
    if not os.path.exists(export_path):
        print(f"Export file not found at {export_path}")
        return False
    
    # Prepare the import file
    files = {
        'formData': (None, '{}', 'application/json'),
        'bundle': ('complete_dashboard.json', open(export_path, 'rb'), 'application/json')
    }
    
    # Import the dashboard
    resp = requests.post(IMPORT_URL, headers=headers, files=files)
    
    if resp.status_code == 200:
        print("Dashboard imported successfully")
        return True
    else:
        print(f"Import failed with status {resp.status_code}: {resp.text}")
        return False

def main():
    print("Waiting for Superset to be ready...")
    time.sleep(10)  # Initial delay to let Superset initialize
    
    print("Importing Marketing Strategy Dashboard...")
    if import_dashboard():
        print("Dashboard import complete!")
        print("Your Marketing Strategy Dashboard is now available with all charts")
    else:
        print("Dashboard import failed. Check the logs above.")

if __name__ == "__main__":
    main() 