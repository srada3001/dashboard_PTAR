"""Local development: SQLite, debug on."""

from .base import *  # noqa: F403
from .base import BASE_DIR, env, sqlite_database

DEBUG = True
SECRET_KEY = env("SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-production")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Serve static files straight from the app folders; no collectstatic needed locally.
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

DATABASES = {"default": sqlite_database(BASE_DIR / "db.sqlite3")}
