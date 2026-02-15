#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput
