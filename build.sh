#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='sultan').exists():
    User.objects.create_superuser('sultan', 'admin@sportstore.com', '123456')
    print('Superuser created: sultan / 123456')
else:
    print('Superuser sultan already exists')
EOF

# Load store data if store_data.json exists and database is empty
python manage.py shell << EOF
from store.models import Product, Category
if Product.objects.count() == 0:
    import json
    from django.core.management import call_command
    print('Loading store data from fixture...')
    call_command('loaddata', 'store_data.json')
    print('Store data loaded successfully!')
else:
    print(f'Database already has {Product.objects.count()} products')
EOF

# Collect static files
python manage.py collectstatic --noinput
