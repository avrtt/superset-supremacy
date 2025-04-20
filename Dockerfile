FROM apache/superset:2.1.0

USER root

# Install additional dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip install --no-cache-dir \
    psycopg2-binary \
    redis \
    flask-cors \
    PyJWT \
    authlib

# Copy configuration files
COPY superset_config.py /app/superset/
COPY ./assets /app/superset/assets/

# Set the proper permissions
RUN chown -R superset:superset /app/superset/assets && \
    chmod -R 777 /app/superset/assets

# Set environment variables
ENV PYTHONPATH=/app/superset
ENV SUPERSET_CONFIG_PATH=/app/superset/superset_config.py
ENV FLASK_APP=superset
ENV FLASK_ENV=production

USER superset

# Initialize the database
RUN superset db upgrade && \
    superset init

EXPOSE 8088

# Use gunicorn as the entrypoint
ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "10", "--timeout", "120", "--limit-request-line", "0", "--limit-request-field_size", "0", "superset.app:create_app()"] 