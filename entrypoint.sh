#!/bin/sh

# Wait for the database to be ready
if [ "$DATABASE" = "postgres" ]; then
    if [ -n "$SQL_INSTANCE_CONNECTION_NAME" ]; then
        echo "Waiting for Cloud SQL..."

        # Start the Cloud SQL Proxy if SQL_INSTANCE_CONNECTION_NAME is set (for Google Cloud)
        /cloud_sql_proxy -dir=/cloudsql -instances=$SQL_INSTANCE_CONNECTION_NAME=tcp:5432 &

        # Wait for the Cloud SQL Proxy to start
        while ! nc -z localhost 5432; do
          sleep 0.1
        done

        echo "Cloud SQL Proxy started"
    else
        echo "Waiting for local Postgres (db container)..."

        # Wait for the local Postgres container (Docker Compose) to be ready
        while ! nc -z db 5432; do
          sleep 0.1
        done

        echo "Local Postgres started"
    fi
fi

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the Gunicorn server
exec gunicorn --bind 0.0.0.0:8080 financial_system.wsgi:application
