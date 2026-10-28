#!/usr/bin/env bash
# Builds the image on Cloud Build and deploys it to Cloud Run. Migrations run when the new
# instance starts. Run from the repo root in Git Bash: bash scripts/gcp/deploy.sh
#
# While a deploy rolls out, the old and new instances overlap for a few seconds: changes made in
# the app during that window are lost. Deploy when nobody is using the dashboard.
set -euo pipefail
cd "$(dirname "$0")/../.."
. scripts/gcp/config.sh
require_project

if [ -n "$(git status --porcelain)" ]; then
    echo "Aviso: hay cambios sin commit; se desplegará el contenido actual de la carpeta." >&2
fi

# Warn if someone used the app in the last 10 minutes.
if gcloud run services describe "$SERVICE" --region "$REGION" >/dev/null 2>&1; then
    RECENT="$(gval logging read "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE\" AND httpRequest.requestMethod:*" \
        --freshness=10m --limit=1 --format='value(timestamp)')"
    if [ -n "$RECENT" ]; then
        echo "Alguien usó el dashboard hace menos de 10 minutos (última petición: $RECENT)."
        echo "Si están guardando datos durante el despliegue, esos cambios se pueden perder."
        read -rp "¿Desplegar de todas formas? [s/N] " ANSWER
        case "$ANSWER" in s|S|si|sí|SI|Sí) ;; *) echo "Despliegue cancelado."; exit 1 ;; esac
    fi
    # A copy of the database before the new version (and its migrations) touches it.
    if [ -z "${SKIP_BACKUP:-}" ]; then
        echo "0/2 Respaldando la base antes de desplegar..."
        if ! bash scripts/gcp/backup.sh; then
            echo "No se pudo respaldar la base; no se desplegó. Corrige el problema o, si de verdad" >&2
            echo "no hace falta el respaldo, despliega con: SKIP_BACKUP=1 bash scripts/gcp/deploy.sh" >&2
            exit 1
        fi
    fi
fi

TAG="$(git rev-parse --short HEAD 2>/dev/null || echo sin-commit)-$(date +%Y%m%d%H%M%S)"

echo "1/2 Construyendo la imagen en Cloud Build ($TAG)..."
gcloud builds submit --tag "$IMAGE:$TAG" .

echo "2/2 Desplegando en Cloud Run..."
# --update-env-vars keeps the variables set by other scripts (LITESTREAM_PATH and the seed of
# replace-db.sh, PTAR_INITIAL_ADMIN): replacing them would bring an old database back.
# One instance only (the SQLite database lives in it) and CPU always allocated, so Litestream
# copies every change to Cloud Storage within about a second. Scales to zero when idle.
# 1 GiB: the filesystem (database, Litestream files, temporary files) lives in memory.
gcloud run deploy "$SERVICE" --image "$IMAGE:$TAG" --region "$REGION" --service-account "$RUN_SA" \
    --allow-unauthenticated --update-env-vars "$APP_ENV" --set-secrets "$APP_SECRETS" \
    --min-instances 0 --max-instances 1 --no-cpu-throttling --execution-environment gen2 \
    --cpu 1 --memory 1Gi

echo "El dashboard está en: $(gval run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')"
