# -*- coding: utf-8 -*-
import os
import sys

import django
from django.core import management

from pathlib import Path


def pytest_configure(config):
    from django.conf import settings
    BASE_DIR = Path(__file__).resolve().parent
    if os.path.exists(str(BASE_DIR) + "/media"):
        for filename in os.listdir(str(BASE_DIR) + "/media"):
            os.remove(str(BASE_DIR) + "/media/" + filename)
    else:
        os.mkdir(str(BASE_DIR) + "/media")

    settings.configure(
        GRAPHENE_DJANGO_CRUD={
            "FILE_TYPE_CONTENT_FIELD_ACTIVE": True,
            "SCALAR_FILTERS_ADD_EQUALS_FIELD" : True
        },
        ALLOWED_HOSTS=["*"],
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        SITE_ID=1,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL="/static/",
        MEDIA_ROOT =str(BASE_DIR  / 'media'),
        MEDIA_URL = '/media/',
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {"debug": True},  # We want template errors to raise
            }
        ],
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "graphene_django",
            "tests",
        ),
        GRAPHENE={
            "SCHEMA": "tests.schema.schema",
        },
        AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
        CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
    )

    django.setup()
    management.call_command("migrate", verbosity=0, interactive=False)

    import graphene
    import graphene_django

    print("django version: " + str(django.VERSION))
    print("graphene version: " + graphene.get_version())
    print("graphene_django version: " + graphene_django.__version__)
