#!/usr/bin/env bash
# One-time setup of the Google Cloud project: APIs, Artifact Registry, Secret Manager,
# the private Cloud Storage bucket and a dedicated service account. Safe to re-run.
# Run from the repo root in Git Bash: bash scripts/gcp/setup.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
. scripts/gcp/config.sh
require_project

echo "Proyecto: $PROJECT_ID · Región: $REGION"

echo "1/5 Activando APIs (puede tardar unos minutos)..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
    secretmanager.googleapis.com storage.googleapis.com logging.googleapis.com

echo "2/5 Repositorio de imágenes (Artifact Registry)..."
if ! gcloud artifacts repositories describe "$REPO" --location="$REGION" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$REPO" --repository-format=docker --location="$REGION"
fi

echo "3/5 Secreto de Django (Secret Manager)..."
if ! gcloud secrets describe "$SECRET_KEY_SECRET" >/dev/null 2>&1; then
    openssl rand -base64 48 | tr -d '\n' \
        | gcloud secrets create "$SECRET_KEY_SECRET" --replication-policy=automatic --data-file=-
fi

echo "4/5 Bucket privado para la base de datos (Cloud Storage)..."
if ! gcloud storage buckets describe "gs://$BUCKET" >/dev/null 2>&1; then
    gcloud storage buckets create "gs://$BUCKET" --location="$REGION" \
        --uniform-bucket-level-access --public-access-prevention
fi
# Object versioning: an overwritten or deleted replica file can still be recovered (REQUISITOS §10).
gcloud storage buckets update "gs://$BUCKET" --versioning >/dev/null

echo "5/5 Cuenta de servicio propia del dashboard y permisos..."
if ! gcloud iam service-accounts describe "$RUN_SA" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$RUN_SA_NAME" --display-name="Dashboard PTAR (Cloud Run)"
fi
# A new service account takes a few seconds to be visible to IAM, so bindings are retried.
retry() {
    for attempt in 1 2 3 4 5 6 7 8 9 10; do
        if "$@" >/dev/null 2>&1; then return 0; fi
        echo "   La cuenta de servicio aún no está lista; reintentando en 10 s ($attempt/10)..."
        sleep 10
    done
    "$@" >/dev/null  # last attempt, showing the error
}
# The dashboard's service account: only its own secret and its own bucket.
retry gcloud secrets add-iam-policy-binding "$SECRET_KEY_SECRET" --member="serviceAccount:$RUN_SA" \
    --role=roles/secretmanager.secretAccessor --condition=None --quiet
retry gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member="serviceAccount:$RUN_SA" \
    --role=roles/storage.objectAdmin
# Cloud Build runs as the project's default compute service account: it reads the uploaded source
# from the <project>_cloudbuild bucket, then builds and pushes the image.
PROJECT_NUMBER="$(gval projects describe "$PROJECT_ID" --format='value(projectNumber)')"
BUILD_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"
for role in roles/cloudbuild.builds.builder roles/artifactregistry.writer roles/logging.logWriter; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$BUILD_SA" \
        --role="$role" --condition=None --quiet >/dev/null
done
SOURCE_BUCKET="gs://${PROJECT_ID}_cloudbuild"
if ! gcloud storage buckets describe "$SOURCE_BUCKET" >/dev/null 2>&1; then
    gcloud storage buckets create "$SOURCE_BUCKET" --location=US --uniform-bucket-level-access
fi
retry gcloud storage buckets add-iam-policy-binding "$SOURCE_BUCKET" --member="serviceAccount:$BUILD_SA" \
    --role=roles/storage.objectViewer

echo "Listo. Siguiente paso: bash scripts/gcp/deploy.sh"
