from pathlib import Path

from core.configuration import (
    DATABASE,
    DEBUG,
    SECRET_KEY,
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = SECRET_KEY

DEBUG = DEBUG

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "psqlextra",
    "django.contrib.gis",
    "django.contrib.postgres",
    "apps.attractions",
]

MIDDLEWARE = []

ROOT_URLCONF = "core.urls"

TEMPLATES = []

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": DATABASE["engine"],
        "NAME": DATABASE["name"],
        "USER": DATABASE["user"],
        "PASSWORD": DATABASE["password"],
        "HOST": DATABASE["host"],
        "PORT": DATABASE["port"],
    }
}

POSTGRES_EXTRA_DB_BACKEND_BASE = "django.contrib.gis.db.backends.postgis"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"