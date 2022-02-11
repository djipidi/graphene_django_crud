# -*- coding: utf-8 -*-
from django.db import models


class Issue8(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
