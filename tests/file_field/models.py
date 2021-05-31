# -*- coding: utf-8 -*-
from django.db import models


class TestFile(models.Model):
    file = models.FileField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)