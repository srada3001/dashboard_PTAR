# Shared names for the Google Cloud scripts. Sourced by setup.sh, deploy.sh and create-admin.sh.
# Override any value by exporting it before running a script (e.g. REGION=southamerica-east1).

# gcloud prints CRLF on Windows; strip it from captured values.
gval() { gcloud "$@" | tr -d '\r'; }

PROJECT_ID="${PROJECT_ID:-$(gval config get-value project 2>/dev/null)}"
REGION="${REGION:-us-east1}"

SERVICE=dashboard-ptar                    # Cloud Run service (the web app, with its SQLite database inside)
REPO=dashboard-ptar                       # Artifact Registry repository
BUCKET="$PROJECT_ID-dashboard-ptar-data"  # Private Cloud Storage bucket: Litestream replica (db/), later exports
SECRET_KEY_SECRET=dashboard-ptar-secret-key
RUN_SA_NAME=dashboard-ptar-run            # Own service account, so other apps in the project can't read the plant data

IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/web"
RUN_SA="$RUN_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# The app answers on its run.app address and, through Firebase Hosting, on refinia-ptar.web.app,
# the address people use (docs/REQUISITOS.md §11 and §15). Firebase forwards the
# request with the run.app Host, so only the browser's Origin needs trusting for CSRF.
APP_ENV="ALLOWED_HOSTS=.run.app,LITESTREAM_BUCKET=$BUCKET,CSRF_TRUSTED_ORIGINS=https://refinia-ptar.web.app"
APP_SECRETS="SECRET_KEY=$SECRET_KEY_SECRET:latest"

# Local backups (backup.sh): the Ecopetrol OneDrive folder, so they also live off this computer.
LITESTREAM_IMAGE=litestream/litestream:0.3.13   # Same version as the Dockerfile
if [ -z "${BACKUP_DIR:-}" ] && command -v cygpath >/dev/null 2>&1; then
    BACKUP_DIR="$(cygpath -u "${OneDriveCommercial:-$HOME/OneDrive - Ecopetrol S.A}")/respaldos/dashboard_ptar"
fi

require_project() {
    if [ -z "$PROJECT_ID" ]; then
        echo "No hay proyecto de Google Cloud activo. Ejecuta: gcloud config set project ID_DEL_PROYECTO" >&2
        exit 1
    fi
}
