from pathlib import Path

DEBUG=True

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "fake-key"

ALLOWED_HOSTS=["*"]

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "graphene_django",
    "tests",
)
TEMPLATES=[
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"debug": True},
    }
]

DATABASES={
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}

GRAPHENE_DJANGO_CRUD = {
    "FILE_TYPE_CONTENT_FIELD_ACTIVE": True,
    "SCALAR_FILTERS_ADD_EQUALS_FIELD": True,
}
GRAPHENE = {
    "SCHEMA": "tests.schema.schema",
}

MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"
STATIC_URL="/static/"

ROOT_URLCONF = "tests.urls"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
