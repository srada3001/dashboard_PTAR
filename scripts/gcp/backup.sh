#!/usr/bin/env bash
# Downloads a copy of the production database and the weekly Excel files to BACKUP_DIR (the
# Ecopetrol OneDrive folder, see config.sh):
#   dashboard_ptar-YYYY-MM-DD_HHMM/dashboard_ptar.sqlite3   the database, ready to open
#   dashboard_ptar-YYYY-MM-DD_HHMM.log                      what was copied
#   exportaciones/                                          every weekly export (only new ones are downloaded)
# Litestream keeps only 3 days of history in the bucket; these copies are the long-term ones.
# deploy.sh runs it before every deploy. Needs gcloud signed in and Docker Desktop running
# (Litestream rebuilds the database in a container).
# Run from Git Bash: bash scripts/gcp/backup.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
. scripts/gcp/config.sh
require_project

if [ -z "${BACKUP_DIR:-}" ]; then
    echo "Falta BACKUP_DIR: la carpeta donde guardar el respaldo." >&2
    exit 1
fi
if ! gcloud auth print-access-token >/dev/null 2>&1; then
    echo "gcloud no tiene una sesión activa. Ejecuta: gcloud auth login" >&2
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    echo "Docker no está corriendo. Abre Docker Desktop y vuelve a intentarlo." >&2
    exit 1
fi

NAME="dashboard_ptar-$(date +%Y-%m-%d_%H%M)"
DEST="$BACKUP_DIR/$NAME"
if [ -e "$DEST" ]; then
    echo "Ya existe $DEST; espera un minuto y vuelve a intentarlo." >&2
    exit 1
fi
mkdir -p "$BACKUP_DIR"
exec > >(tee "$BACKUP_DIR/$NAME.log") 2>&1

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The replica folder the service uses now: replace-db.sh starts a new one (LITESTREAM_PATH).
REPLICA="$(gval run services describe "$SERVICE" --region "$REGION" --format=json \
    | uv run python -c "import json, sys; env = json.load(sys.stdin)['spec']['template']['spec']['containers'][0].get('env', []); print(next((e.get('value', '') for e in env if e['name'] == 'LITESTREAM_PATH'), 'db'))")"

echo "Respaldo del dashboard PTAR en $DEST"
echo "1/4 Buscando la copia actual de la base en gs://$BUCKET/$REPLICA..."
# Every start of the container begins a new Litestream generation; the current one is the one
# changed last, and it is all that is needed to rebuild the database (the whole replica is >1 GB).
GENERATION="$(gval storage ls -l -r "gs://$BUCKET/$REPLICA/generations/" | uv run python -c "
import sys
newest = max((line.split() for line in sys.stdin if '/generations/' in line and len(line.split()) == 3),
             key=lambda parts: parts[1])
print(newest[2].split('/generations/')[1].split('/')[0])
")"
echo "  Generación $GENERATION"

echo "2/4 Descargando esa generación..."
mkdir -p "$WORK/replica/generations"
gcloud storage cp -r "gs://$BUCKET/$REPLICA/generations/$GENERATION" "$WORK/replica/generations/"

echo "3/4 Reconstruyendo la base con Litestream..."
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -w "$WORK"):/work" "$LITESTREAM_IMAGE" \
    restore -generation "$GENERATION" -o /work/dashboard_ptar.sqlite3 file:///work/replica
PYTHONIOENCODING=utf-8 uv run python - "$WORK/dashboard_ptar.sqlite3" <<'EOF'
import sqlite3
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

connection = sqlite3.connect(sys.argv[1])
if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
    sys.exit("La base reconstruida está dañada; no se guardó el respaldo.")
count = lambda table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
# Captures and corrections go to the measurement history; the rest, to the audit log.
last = connection.execute(
    "SELECT max(t) FROM (SELECT max(timestamp) AS t FROM core_auditentry"
    " UNION ALL SELECT max(timestamp) FROM measurements_measurementhistory)"
).fetchone()[0]
if last:
    last = datetime.fromisoformat(last).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Bogota"))
    last = f"{last:%Y-%m-%d %H:%M}"
print(f"  Íntegra. Mediciones: {count('measurements_measurement')} · Personas: {count('accounts_user')} · Último cambio: {last or '—'}")
connection.close()
EOF
mkdir -p "$DEST"
mv "$WORK/dashboard_ptar.sqlite3" "$DEST/"

echo "4/4 Descargando las exportaciones semanales nuevas a $BACKUP_DIR/exportaciones..."
# Each weekly file has all the data up to its Sunday, so they are kept once, not in every backup.
if gcloud storage ls "gs://$BUCKET/exports/" >/dev/null 2>&1; then
    mkdir -p "$BACKUP_DIR/exportaciones"
    gcloud storage cp --no-clobber "gs://$BUCKET/exports/*" "$BACKUP_DIR/exportaciones/"
fi

echo "Listo: $DEST ($(du -sh "$DEST" | cut -f1))"
