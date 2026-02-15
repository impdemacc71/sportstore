#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput
