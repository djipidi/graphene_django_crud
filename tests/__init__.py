# -*- coding: utf-8 -*-

# Horrific monkey patch
import django.utils.encoding
django.utils.encoding.force_text = django.utils.encoding.force_str

default_app_config = 'tests.apps.GDCTestConfig'
