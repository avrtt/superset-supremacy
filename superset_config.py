import os
from datetime import timedelta
from flask_appbuilder.security.manager import AUTH_OAUTH
from superset.security import SupersetSecurityManager

# Database connection settings
SQLALCHEMY_DATABASE_URI = os.environ.get("SUPERSET_DB_URI", "sqlite:////app/superset_home/superset.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# General configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "thisISaSECRET_1234")
APP_NAME = "Marketing Strategy Dashboard"
ENABLE_PROXY_FIX = True

# Redis cache for dashboard queries
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,  # 1 day default
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': os.environ.get("REDIS_URL", "redis://redis:6379/0"),
}

# Flask-Caching for server-side cache (heavy queries)
FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24 * 7,  # 1 week
    'CACHE_KEY_PREFIX': 'filter_state_',
    'CACHE_REDIS_URL': os.environ.get("REDIS_URL", "redis://redis:6379/1"),
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,  # 1 day
    'CACHE_KEY_PREFIX': 'data_cache_',
    'CACHE_REDIS_URL': os.environ.get("REDIS_URL", "redis://redis:6379/2"),
}

# Custom dark theme configuration
CUSTOM_THEME = {
    "name": "Marketing Strategy Dark",
    "backgroundColor": "#121212",
    "backgroundColorLight": "#1e1e1e",
    "backgroundColorDark": "#0a0a0a",
    "borderColor": "#2c2c2c",
    "gridLineColor": "#2c2c2c",
    "textColor": "#ffffff",
    "textColorLight": "#e0e0e0",
    "textColorDark": "#c0c0c0",
    "primaryColor": "#2196f3",
    "secondaryColor": "#4caf50",
    "tertiaryColor": "#ff9800",
}

# Apply custom theme as default
DEFAULT_THEME = "Marketing Strategy Dark"

# Feature toggles
FEATURE_FLAGS = {
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "ALERT_REPORTS": True,
    "DASHBOARD_CACHE": True,
    "ALLOW_ADHOC_SUBQUERY": True,
    "GLOBAL_ASYNC_QUERIES": True,
    "ENABLE_JAVASCRIPT_CONTROLS": True,
}

# Security settings - enable RBAC for dashboards
DASHBOARD_RBAC = True
FAB_ROLES = {
    "Admin": [
        ["can_read", "Dashboard"],
        ["can_write", "Dashboard"],
        ["can_read", "Chart"],
        ["can_write", "Chart"],
        ["can_read", "Dataset"],
        ["can_write", "Dataset"],
        ["can_read", "Database"],
        ["can_write", "Database"],
    ],
    "Analyst": [
        ["can_read", "Dashboard"],
        ["can_read", "Chart"],
        ["can_read", "Dataset"],
        ["can_read", "Database"],
    ],
}

# OAuth2 configuration example
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs': {
                'scope': 'email profile'
            },
            'request_token_url': None,
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        }
    }
]

# JWT token configuration
class CustomSecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(CustomSecurityManager, self).__init__(appbuilder)
        self.jwt_exp_delta_seconds = 60 * 60 * 24  # JWT expiration time (1 day)

CUSTOM_SECURITY_MANAGER = CustomSecurityManager

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

# Default query limit
SQL_MAX_ROW = 100000
DEFAULT_SQLLAB_LIMIT = 1000

# Query time limit
SQLLAB_TIMEOUT = 60 * 60  # 1 hour
SUPERSET_WEBSERVER_TIMEOUT = 60 * 60  # 1 hour

# Enable server-side pagination
TABLE_VIZ_ROW_LIMIT = 10000

# Results backend configuration
RESULTS_BACKEND = {
    "type": "redis",
    "url": os.environ.get("REDIS_URL", "redis://redis:6379/3"),
}

# Email reports
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your-password")
SMTP_MAIL_FROM = os.environ.get("SMTP_MAIL_FROM", "reports@yourdomain.com")

# Superset specific configurations
ENABLE_SCHEDULED_EMAIL_REPORTS = True
EMAIL_REPORTS_CRON_RESOLUTION = 15  # minutes
EMAIL_ASYNC_TIME_LIMIT_SEC = 300  # 5 minutes
EMAIL_REPORT_INACTIVITY_TIME = 180  # 180 days

# Alerts and scheduled reports
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-setuid-sandbox",
    "--disable-extensions",
] 