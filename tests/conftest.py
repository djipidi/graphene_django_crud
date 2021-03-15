# -*- coding: utf-8 -*-
import os
import sys

import django
from django.core import management


def pytest_addoption(parser):
    parser.addoption(
        "--no-pkgroot",
        action="store_true",
        default=False,
        help="Remove package root directory from sys.path, ensuring that "
        "graphene_django_extras is imported from the installed site-packages. "
        "Used for testing the distribution.",
    )
    parser.addoption(
        "--staticfiles",
        action="store_true",
        default=False,
        help="Run tests with static files collection, using manifest "
        "staticfiles storage. Used for testing the distribution.",
    )


def pytest_configure(config):
    from django.conf import settings
    settings.configure(
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
        AUTHENTICATION_BACKENDS=(
            "django.contrib.auth.backends.ModelBackend",
        ),
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "channels.layers.InMemoryChannelLayer"
            }
        }
    )

    django.setup()
    management.call_command("migrate", verbosity=0, interactive=False)
    if config.getoption("--staticfiles"):
        management.call_command("collectstatic", verbosity=0, interactive=False)

    import graphene
    import graphene_django

    print("django version: " + str(django.VERSION))
    print("graphene version: " + graphene.get_version())
    print("graphene_django version: " + graphene_django.__version__)