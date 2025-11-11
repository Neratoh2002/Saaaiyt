INSTALLED_APPS = [
    # стандартные
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # сторонние
    "rest_framework",

    # наше приложение
    "shop",
]

# Шаблоны (добавьте 'DIRS': [BASE_DIR / "shop" / "templates"] если нужно)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "shop" / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "shop" / "static"]  # чтобы брать css/js из app/static
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# DRF (минимально)
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}
