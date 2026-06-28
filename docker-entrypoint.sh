#!/bin/bash
set -e

echo "Running migrations..."
python backend/manage.py migrate --noinput

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput --clear

echo "Starting gunicorn..."
exec gunicorn --chdir backend privai_django.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --threads 2 \
    --timeout 600 \
    --max-requests 1 \
    --log-level info \
    --preload
