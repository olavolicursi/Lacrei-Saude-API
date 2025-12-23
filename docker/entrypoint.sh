#!/bin/bash
# docker/entrypoint.sh

set -e

echo "🔍 Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ PostgreSQL started"

echo "� Creating necessary directories and files..."
mkdir -p /app/logs /app/staticfiles /app/media
touch /app/logs/api.log /app/logs/errors.log /app/logs/security.log
chmod -R 777 /app/logs

echo "�🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "👤 Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@lacrei.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superuser "{username}" created successfully')
else:
    print(f'ℹ️  Superuser "{username}" already exists')
END

echo "🚀 Starting application..."
exec "$@"
