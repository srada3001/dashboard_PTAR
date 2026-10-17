#!/bin/sh
# Container startup on Cloud Run:
#   1. restore the SQLite database from Cloud Storage (if this instance has no copy yet),
#   2. apply migrations and create the first administrator if requested,
#   3. serve the app while Litestream replicates every change to Cloud Storage (~1 s).
# Needs a single instance and "CPU always allocated" (see scripts/gcp/deploy.sh).
set -e

for var in LITESTREAM_BUCKET SECRET_KEY ALLOWED_HOSTS; do
    eval "value=\${$var:-}"
    if [ -z "$value" ]; then
        echo "Falta la variable $var. Despliega con scripts/gcp/deploy.sh (después de scripts/gcp/setup.sh)." >&2
        exit 1
    fi
done

CONFIG=/app/docker/litestream.yml
mkdir -p "$(dirname "$DATABASE_PATH")"

litestream restore -config "$CONFIG" -if-db-not-exists -if-replica-exists "$DATABASE_PATH"

python manage.py migrate --noinput
python manage.py create_initial_admin --from-env

exec litestream replicate -config "$CONFIG" -exec \
    "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 300 --access-logfile -"
