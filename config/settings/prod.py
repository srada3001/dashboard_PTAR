"""Production on Google Cloud Run. SQLite + Litestream (replica in Cloud Storage);
SECRET_KEY comes from Secret Manager through an environment variable."""

from .base import *  # noqa: F403
from .base import env, sqlite_database

SECRET_KEY = env("SECRET_KEY")
# On Cloud Run use ".run.app": Google's front end only routes this service's own *.run.app
# hostnames to it, so any other Host never reaches the app.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
# Behind Firebase Hosting the browser's Origin is https://refinia-ptar.web.app while the Host is
# the run.app one, so that origin must be trusted for forms to pass the CSRF check.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# SQLite file inside the container, continuously replicated to Cloud Storage by Litestream
# (see docker/start.sh). Requires a single Cloud Run instance.
DATABASES = {"default": sqlite_database(env("DATABASE_PATH", default="/data/db.sqlite3"))}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# HTTPS is terminated by Google's front end.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# HSTS preload only makes sense for a domain we own; the app runs on Google-provided hosts.
SILENCED_SYSTEM_CHECKS = [*SILENCED_SYSTEM_CHECKS, "security.W021"]  # noqa: F405

# Google's front end sits in front of the app, so axes records the real client IP.
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
