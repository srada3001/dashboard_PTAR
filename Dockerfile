# Image for the dashboard-ptar Cloud Run service. Built remotely by Cloud Build: scripts/gcp/deploy.sh
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

# Litestream (static binary) replicates the SQLite database to Cloud Storage.
ARG LITESTREAM_VERSION=0.3.13
ADD https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-amd64.tar.gz /tmp/litestream.tar.gz
RUN tar -xzf /tmp/litestream.tar.gz -C /usr/local/bin litestream && rm /tmp/litestream.tar.gz \
    && litestream version

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    DATABASE_PATH=/data/db.sqlite3

WORKDIR /app

# Dependencies first, so code changes don't reinstall them.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

# Collect the static files at build time. The values only satisfy prod settings.
RUN SECRET_KEY=build-only ALLOWED_HOSTS=localhost python manage.py collectstatic --noinput

RUN chmod +x docker/start.sh \
    && useradd --system --uid 1000 --home /app app \
    && mkdir -p /data && chown -R app /app /data
USER app

CMD ["/app/docker/start.sh"]
