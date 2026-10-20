"""Settings shared by every environment."""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("SECRET_KEY", default="")
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "apps.catalog",
    "apps.accounts",
    "apps.core",
    "apps.measurements",
    "apps.imports",
    "apps.capture",
    "apps.dashboards",
    "apps.exports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # After WhiteNoise, so static files keep their own (public) caching headers.
    "apps.core.middleware.PrivateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Outside the auth middlewares, so it also sees their redirects.
    "apps.core.middleware.HtmxRedirectMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.accounts.middleware.ForcePasswordChangeMiddleware",
    # Starts each Monday's export after the first request that finds it due (apps/exports/weekly.py).
    "apps.exports.middleware.WeeklyExportMiddleware",
    # Must be last, per django-axes docs.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Auth
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# The app may be served behind Firebase Hosting (refinia-ptar.web.app), which only forwards the
# cookie named "__session" to Cloud Run. So the session uses that name and the CSRF token lives in
# the session instead of its own cookie. Both work the same when the app is reached on run.app.
SESSION_COOKIE_NAME = "__session"
CSRF_USE_SESSIONS = True

# Account lockout: 10 consecutive failures lock the *account* (not the IP, since a whole control
# room may share one public IP) for exactly 10 minutes.
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(minutes=10)
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False
AXES_LOCKOUT_TEMPLATE = "registration/locked.html"
# axes.W006 warns that username-only lockout does not throttle by IP; that is intended here.
SILENCED_SYSTEM_CHECKS = ["axes.W006"]

# i18n
LANGUAGE_CODE = "es"  # es-co's catalog is less complete (untranslated admin strings)
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Exports (docs/REQUISITOS.md §10): files go to the exports/ folder of this bucket when it is set
# (production), else to the exports/ folder of the repository. Each Monday's file is prepared by
# itself unless WEEKLY_EXPORT_AUTO is off.
EXPORTS_BUCKET = ""
EXPORTS_DIR = BASE_DIR / "exports"
WEEKLY_EXPORT_AUTO = True


def sqlite_database(path):
    """SQLite tuned for a small multi-threaded web app (and Litestream in production):
    WAL journal, IMMEDIATE transactions to avoid lock upgrades, and a generous busy timeout."""
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(path),
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    }
