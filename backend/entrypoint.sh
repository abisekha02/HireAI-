#!/bin/sh
set -e

echo "Waiting for database..."
python - << 'PYEOF'
import os
import time
import psycopg2

for _ in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "hireai"),
            user=os.environ.get("POSTGRES_USER", "hireai"),
            password=os.environ.get("POSTGRES_PASSWORD", "hireai"),
            host=os.environ.get("POSTGRES_HOST", "db"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
        ).close()
        break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    raise SystemExit("Database never became available")
PYEOF

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

exec "$@"
