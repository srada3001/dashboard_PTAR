#!/bin/sh
# Container startup on Cloud Run:
#   1. restore the SQLite database from Cloud Storage (if this instance has no copy yet) or, the
#      first time after scripts/gcp/replace-db.sh, download the database that replaces it,
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
# Folder of the replica in the bucket. replace-db.sh starts a new one, so the old one is kept.
export LITESTREAM_PATH="${LITESTREAM_PATH:-db}"

litestream restore -config "$CONFIG" -if-db-not-exists -if-replica-exists "$DATABASE_PATH"

# A replaced database (replace-db.sh) has no replica yet: it starts from the file uploaded.
# Once Litestream has replicated it, the replica exists and is restored instead.
if [ ! -f "$DATABASE_PATH" ] && [ -n "${PTAR_SEED_DB:-}" ]; then
    python docker/fetch_seed.py "$LITESTREAM_BUCKET" "$PTAR_SEED_DB" "$DATABASE_PATH" "${PTAR_SEED_SHA256:-}"
fi

python manage.py migrate --noinput
python manage.py create_initial_admin --from-env

exec litestream replicate -config "$CONFIG" -exec \
    "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 300 --access-logfile -"
