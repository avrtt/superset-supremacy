#!/usr/bin/env python

import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database configuration
DB_URI = os.environ.get('SUPERSET_DB_URI', 'postgresql://superset:superset@postgres:5432/marketing_analytics')

# Function to execute a SQL query and return results
def execute_query(query, fetch=True):
    engine = create_engine(DB_URI)
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            if fetch:
                return result.fetchall()
            return True
    except SQLAlchemyError as e:
        print(f"Error executing query: {e}")
        return None

# Function to check if materialized views exist
def check_materialized_views():
    query = """
    SELECT matviewname FROM pg_matviews
    WHERE schemaname = 'public'
    ORDER BY matviewname;
    """
    results = execute_query(query)
    if results:
        print("Found materialized views:")
        for row in results:
            print(f"- {row[0]}")
        return True
    else:
        print("No materialized views found.")
        return False

# Function to create materialized views if they don't exist
def create_materialized_views():
    # Read the SQL file content
    try:
        with open('/docker-entrypoint-initdb.d/marketing_metrics_materialized_views.sql', 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL to create materialized views
        result = execute_query(sql_content, fetch=False)
        if result:
            print("Successfully created materialized views")
            return True
        else:
            print("Failed to create materialized views")
            return False
    except FileNotFoundError:
        print("Could not find the SQL file for materialized views")
        return False

def main():
    print("Checking materialized views...")
    if not check_materialized_views():
        print("Creating materialized views...")
        if not create_materialized_views():
            print("Failed to create materialized views. Exiting.")
            return
    
    print("\nMaterialized views are ready.")
    print("\nTo create datasets and charts in Superset:")
    print("1. Log in to Superset at http://localhost:8088 (admin/admin)")
    print("2. Go to Data -> Datasets")
    print("3. Click '+ Dataset'")
    print("4. Select 'Marketing Analytics' database")
    print("5. Select 'public' schema")
    print("6. Add these tables one by one:")
    print("   - mv_daily_channel_metrics")
    print("   - mv_funnel_conversion_rates")
    print("   - mv_budget_vs_actual")
    print("   - mv_forecast_accuracy")
    print("\nAfter creating datasets, create charts using these metrics:")
    print("1. For mv_daily_channel_metrics:")
    print("   - Average ROI")
    print("   - Average ROAS")
    print("   - Average CAC")
    print("   - Total Spend")
    print("2. For mv_funnel_conversion_rates:")
    print("   - Funnel visualization with awareness, consideration, decision, and conversion stages")
    print("   - Conversion rates by channel")
    print("3. For mv_budget_vs_actual:")
    print("   - Budget vs actual spend by channel")
    print("   - Budget utilization percentages")
    print("4. For mv_forecast_accuracy:")
    print("   - Forecast accuracy percentage")
    print("   - Predicted vs actual ROI time series")
    
if __name__ == "__main__":
    main() 