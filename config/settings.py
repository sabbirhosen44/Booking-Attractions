from pathlib import Path

from config.configuration import (
    DATABASE,
    DEBUG,
    SECRET_KEY,
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = SECRET_KEY

DEBUG = DEBUG

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "attractions",
]

MIDDLEWARE = []

ROOT_URLCONF = "config.urls"

TEMPLATES = []

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": DATABASE["engine"],
        "NAME": BASE_DIR / DATABASE["name"],
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"