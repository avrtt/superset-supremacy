Another one of my "prototype" dashboards, built with Apache Superset as part of freelance work (in marketing analytics for strategic decision-making).

Notes:
1. Original data has been replaced for privacy purposes.
2. Many features and design elements have been changed (this is basically a quickly made replica of my own dashbord for portfolio).
3. I've kept the deployment process and other DevOps stuff, as well as the core architecture.

You may find this repo useful when you need to quickly deploy Superset dashboards inside Docker, with K8S orchestration, CI/CD workflows, easy DB integrations, etc.

[Here](https://github.com/avrtt/dashbordina) is my Dash prototype with Airflow for ETL and RESTful endpoints.

Features:

- **Strategic Marketing KPIs**: Monitor ROI, ROAS, CAC, and CLV metrics in real-time
- **Channel Performance Analysis**: Compare effectiveness across marketing channels with visualizations
- **Marketing Funnel Visualization**: Track conversion rates at each stage of the marketing funnel
- **Budget Analysis**: Compare planned vs actual spending with utilization metrics
- **ROI Forecasting**: Analyze forecast accuracy and compare predicted vs actual ROI
- **Interactive Filters**: Filter data by date range, channel, and other dimensions
- **Dark Mode Interface**: Modern dark-themed UI for better visual contrast and reduced eye strain
- **Responsive Layout**: Optimized for both desktop and mobile viewing
- **Data Integration**: Direct connection to PostgreSQL database with materialized views
- **Performance Optimized**: Server-side caching and materialized views for fast query responses

## Components

The dashboard provides a view of marketing performance with the following visualizations:

### KPI metrics
- **Total Marketing Spend**: Sum of all marketing expenditures
- **Overall ROAS**: Return on Ad Spend across all channels
- **Overall ROI**: Return on Investment percentage
- **Average CAC**: Customer Acquisition Cost across channels
- **Forecast Accuracy**: Model prediction accuracy percentage

### Channel performance
- **ROI Trend by Channel**: Time series analysis of ROI performance by marketing channel
- **Channel ROI Comparison**: Donut chart comparing ROI across channels
- **CAC by channel**: Bar chart of Customer Acquisition Cost by channel

### Funnel analysis
- **Marketing Funnel**: Visualization of user journey from awareness to conversion
- **Conversion Rates by Channel**: Bar chart showing conversion rates at each funnel stage by channel

### Budget analysis
- **Budget vs Actual Spend**: Bar chart comparing planned and actual spending by channel
- **Budget Utilization**: Channel-specific budget utilization percentage

### ROI forecasting
- **Predicted vs Actual ROI**: Time series comparison of forecast vs actual ROI
- **Forecast Accuracy Trend**: Line chart showing forecast accuracy over time

## Screenshots (minimal version)

![1](/screenshots/1.png)
![2](/screenshots/2.png)
![3](/screenshots/3.png)
![4](/screenshots/4.png)

## Setup instructions

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database with marketing data tables
- Git
- For Kubernetes deployment: Kubectl and access to a Kubernetes cluster

If required, don't forget to enable/start Docker daemon and reboot your computer.

### Minimal (demo) mode

Minimal zero-config demo mode lets you try it instantly:

```bash
# Clone the repository
git clone https://github.com/avrtt/superset-supremacy.git
cd superset-supremacy

# Run the quick demo script
./quick-demo.sh

# Access Superset at http://localhost:8088
# Default credentials: admin / admin
```

This will automatically:
- Start a clean demo environment using Docker
- Configure everything with no input required
- Create a demo admin user
- Set up the database with marketing sample data
- Launch the dashboard in development mode

<br>

![5](/screenshots/5.png)

<br>

**Note**: The demo may take a minute to fully initialize. You can check the status with:
```bash
docker logs -f demo_superset
```

If you need to populate the dashboard with charts manually, follow the step-by-step guide in [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

To stop the demo:
```bash
docker-compose -f docker-compose-demo.yml down -v
```

The demo uses completely separate Docker volumes, so it won't interfere with any production setup you might create later.

### Standard setup

1. Clone this repository:
```bash
git clone https://github.com/avrtt/superset-supremacy.git
cd superset-supremacy
```

2. Configure environment variables in `.env` file (copy from `.env.example`)

3. Start the services:
```bash
docker-compose up -d
```

4. Access Superset at `http://localhost:8088`
   - Default credentials: admin/admin

### Kubernetes deployment

For production deployment, Kubernetes manifests are provided in the `kubernetes/` directory:

```bash
# Create namespace and resources
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml # Make sure to update with your actual secrets
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml # Update the host as needed
```

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### DB setup

1. Connect to your PostgreSQL instance:
   - Go to "Data → Databases" in the Superset UI
   - Click "+ Database" and select "PostgreSQL"
   - Configure the connection string and test the connection

2. Import the included dataset definitions:
   - Go to "Data → Datasets"
   - Import the JSON definitions from `assets/datasets/`

### Customization

You can customize the dashboard in several ways:

1. **Through Superset UI**:
   - Log in to Superset
   - Navigate to the Marketing Strategy Dashboard
   - Click "Edit Dashboard" to modify layout and components
   - Add filters, rearrange charts, or modify chart properties

2. **Through API and Scripts**:
   - Modify `sql/create_charts_and_add_to_dashboard.py` to adjust chart configurations
   - Add new chart types or modify existing ones
   - Change color schemes, labels, or visualization properties

3. **Theming**:
   - Edit `superset_config.py` to adjust global theme settings
   - Modify CSS in dashboard JSON metadata for dashboard-specific theming

## Data architecture

The dashboard uses a star schema data model centered around marketing campaigns with the following materialized views:

1. **mv_daily_channel_metrics**: Performance metrics by channel (ROI, ROAS, CAC, CLV)
2. **mv_funnel_conversion_rates**: Funnel stage metrics and conversion rates
3. **mv_budget_vs_actual**: Budget allocation and utilization metrics
4. **mv_forecast_accuracy**: Forecast vs actual performance metrics

These materialized views are refreshed daily for optimal performance while providing up-to-date metrics.

## Theming

The dashboard uses a custom dark theme with the following properties:
- Background: #121212
- Text: High-contrast (white/light gray)
- Accent colors: Blue/green for metrics and visualizations

Theme configuration is applied in `superset_config.py`.

## Authentication & authorization

The dashboard implements Superset's Flask AppBuilder (FAB) Role-Based Access Control:
- `Admin`: Full access to all dashboard features
- `Analyst`: Read-only access to dashboards and charts

OAuth2/JWT integration is available for enterprise SSO.

## CI/CD

A GitHub Actions workflow is included for:
- Building and testing the Docker image
- Pushing to container registry
- Deploying to AWS ECS/EKS

See `.github/workflows/ci.yml` for details.

## Project structure

```
.
├── assets/ # Dashboard and dataset exports
│   ├── dashboards/ # Dashboard JSON definitions
│   └── datasets/ # Dataset JSON definitions
├── sql/ # SQL scripts and utilities
│   ├── create_charts_and_add_to_dashboard.py # Python script to create charts via API
│   ├── create_marketing_dashboard.py # Dashboard creation script
│   ├── marketing_analysis_examples.sql # Example SQL queries
│   ├── marketing_metrics_materialized_views.sql # Materialized view definitions
│   └── sample_data.sql # Sample data for demo
├── kubernetes/ # Kubernetes deployment manifests
├── .github/workflows/ # CI/CD pipeline definitions
├── superset_config.py # Superset configuration
├── docker-compose.yml # Production setup
├── docker-compose-demo.yml # Demo environment setup
├── quick-demo.sh # Quick start demo script
├── DASHBOARD_SETUP.md # Step-by-step guide for dashboard setup
└── DEPLOYMENT.md # Detailed deployment instructions
```

## Troubleshooting

[This](https://wiki.archlinux.org/title/Docker#Troubleshooting) may be helpful for Arch users when having problems with Docker setup.

Common issues:
- **Empty dashboard**: Follow the [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) guide to create datasets and charts
- **Missing datasets**: Ensure materialized views are created in the database
- **Slow performance**: Check materialized view refresh status and consider adjusting refresh frequency

## License

Apache 2.0.