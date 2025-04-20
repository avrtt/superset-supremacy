#!/bin/bash
set -e

echo "🚀 Starting Superset Marketing Dashboard in DEMO mode..."
echo "⚠️  This is for demonstration purposes only - not for production use!"

# Clean up any previous demo containers
echo "Cleaning up any previous demo containers..."
docker-compose -f docker-compose-demo.yml down -v 2>/dev/null || true

# Start the services using the demo compose file
echo "Starting services with demo configuration..."
docker-compose -f docker-compose-demo.yml up -d

echo -e "\n✅ Demo started successfully!"
echo "📊 Access the dashboard at: http://localhost:8088"
echo "🔑 Default credentials: admin / admin"
echo "ℹ️  It may take a minute for Superset to initialize. Check status with: docker logs -f demo_superset"
echo "🔄 If Superset fails to start, try: docker-compose -f docker-compose-demo.yml restart superset"

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Execute SQL scripts directly on the database
echo "Setting up database tables and sample data..."
# First create and populate sample tables
docker exec demo_postgres psql -U superset -d marketing_analytics -f /docker-entrypoint-initdb.d/sample_data.sql
# Then create materialized views
docker exec demo_postgres psql -U superset -d marketing_analytics -f /docker-entrypoint-initdb.d/marketing_metrics_materialized_views.sql

echo -e "\n🔄 Wait for Superset to fully initialize (about 30 seconds)..."
sleep 30

echo -e "\n📊 Creating Marketing Dashboard..."
# Install Python dependencies inside container
docker exec demo_superset pip install requests sqlalchemy

# Copy the Python script to the container
docker cp sql/create_marketing_dashboard.py demo_superset:/app/create_marketing_dashboard.py

# Execute the Python script inside the container
docker exec demo_superset python /app/create_marketing_dashboard.py

echo -e "\n📝 Manual setup instructions:"
echo "1. Log in to Superset at http://localhost:8088 with admin/admin"
echo "2. Go to Data -> Databases and verify 'Marketing Analytics' database exists"
echo "3. Go to Data -> Datasets and create new datasets for these tables:"
echo "   - mv_daily_channel_metrics"
echo "   - mv_funnel_conversion_rates"
echo "   - mv_budget_vs_actual"
echo "   - mv_forecast_accuracy"
echo "4. Create charts using the examples in sql/marketing_analysis_examples.sql"
echo "5. Add the charts to your 'Marketing Strategy Dashboard'"
echo -e "\n📋 To stop the demo, run: docker-compose -f docker-compose-demo.yml down -v"
echo "📝 For production setup, see README.md for standard setup instructions" 