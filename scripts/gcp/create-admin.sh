#!/usr/bin/env bash
# Creates the first administrator: the app creates it at startup with a random temporary
# password, shown here once, which must be changed at first login. Run after deploy.sh,
# from the repo root in Git Bash: bash scripts/gcp/create-admin.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
. scripts/gcp/config.sh
require_project

read -rp "Usuario (nombre corto, sin espacios): " USERNAME
read -rp "Nombre completo (sin comas ni punto y coma): " FULL_NAME

# Restarts the service with the request; the app creates the admin only if none exists yet.
gcloud run services update "$SERVICE" --region "$REGION" \
    --update-env-vars "PTAR_INITIAL_ADMIN=$USERNAME;$FULL_NAME"

echo "Buscando la contraseña temporal en los logs (puede tardar unos segundos)..."
for _ in 1 2 3 4 5 6 7 8 9; do
    OUTPUT="$(gval logging read "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE\" AND textPayload:\"Contraseña temporal\"" \
        --freshness=15m --limit=1 --format='value(textPayload)')"
    if [ -n "$OUTPUT" ]; then
        printf '%s\n' "$OUTPUT"
        echo "Entra al dashboard con ese usuario y contraseña; la app te pedirá cambiarla."
        exit 0
    fi
    sleep 10
done
echo "No apareció todavía. Búscala en Cloud Run → $SERVICE → Logs (texto: Contraseña temporal)." >&2
echo "Si ya existía un administrador, no se crea otro." >&2
