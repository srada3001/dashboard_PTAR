#!/usr/bin/env bash
# Replaces the production database with a local SQLite file: the historical import is run and
# reviewed locally, and then the local database goes to production (docs/REQUISITOS.md §9).
# Whatever was created in production is left out, and everything in the local file goes, its
# users included. The old replica stays in the bucket, so it can be brought back.
# Run from the repo root in Git Bash: bash scripts/gcp/replace-db.sh [db.sqlite3]
set -euo pipefail
cd "$(dirname "$0")/../.."
. scripts/gcp/config.sh
require_project

SOURCE="${1:-db.sqlite3}"
if [ ! -f "$SOURCE" ]; then
    echo "No existe $SOURCE." >&2
    exit 1
fi

STAMP="$(date +%Y%m%d%H%M%S)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
SEED="$WORK/db.sqlite3"

echo "1/3 Revisando y compactando $SOURCE..."
# A single clean file (no WAL), checked, with a summary of what goes to production.
uv run python - "$SOURCE" "$SEED" <<'EOF'
import sqlite3
import sys

source, target = sys.argv[1:]
connection = sqlite3.connect(source)
if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
    sys.exit(f"{source} está dañada.")
connection.execute("VACUUM INTO ?", (target,))
count = lambda table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
print(f"  Mediciones: {count('measurements_measurement')}")
print(f"  Variables: {count('catalog_variable')}")
users = connection.execute("SELECT username, role, is_active FROM accounts_user ORDER BY username").fetchall()
print("  Personas: " + ", ".join(f"{u} ({r}{'' if a else ', inactiva'})" for u, r, a in users))
connection.close()
EOF
SHA256="$(sha256sum "$SEED" | cut -d' ' -f1)"
echo "  Tamaño: $(du -h "$SEED" | cut -f1)"

CURRENT_PATH="$(gval run services describe "$SERVICE" --region "$REGION" --format=json \
    | uv run python -c "import json, sys; env = json.load(sys.stdin)['spec']['template']['spec']['containers'][0].get('env', []); print(next((e.get('value', '') for e in env if e['name'] == 'LITESTREAM_PATH'), 'db'))")"

echo
echo "Esto REEMPLAZA la base de producción por $SOURCE."
echo "Lo que se haya creado en producción no pasa a la nueva base (queda en gs://$BUCKET/$CURRENT_PATH)."
RECENT="$(gval logging read "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE\" AND httpRequest.requestMethod:*" \
    --freshness=10m --limit=1 --format='value(timestamp)')"
if [ -n "$RECENT" ]; then
    echo "Alguien usó el dashboard hace menos de 10 minutos (última petición: $RECENT)."
fi
read -rp "Escribe «reemplazar» para continuar: " ANSWER
if [ "$ANSWER" != "reemplazar" ]; then
    echo "Cancelado; no se cambió nada."
    exit 1
fi

echo "2/3 Subiendo la base a gs://$BUCKET/seed/$STAMP.sqlite3..."
gcloud storage cp "$SEED" "gs://$BUCKET/seed/$STAMP.sqlite3"

echo "3/3 Reiniciando el servicio con la base nueva..."
# A new replica folder: the new revision finds no replica there, downloads the seed and starts
# replicating it. The folder of the old database is left as it is.
gcloud run services update "$SERVICE" --region "$REGION" \
    --update-env-vars "LITESTREAM_PATH=db-$STAMP,PTAR_SEED_DB=seed/$STAMP.sqlite3,PTAR_SEED_SHA256=$SHA256"

echo
echo "Listo. La base de producción es ahora la de $SOURCE (réplica en gs://$BUCKET/db-$STAMP)."
echo "Para volver a la anterior:"
echo "  gcloud run services update $SERVICE --region $REGION --update-env-vars LITESTREAM_PATH=$CURRENT_PATH"
