#!/bin/sh
set -e

echo "Making migrations..."
python manage.py makemigrations accounts todos --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
