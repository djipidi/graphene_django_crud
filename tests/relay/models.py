# -*- coding: utf-8 -*-
from django.db import models


class TestRelayA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_relay_b = models.ForeignKey(
        "testRelayB", on_delete=models.CASCADE, related_name="test_relay_as"
    )



class TestRelayB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
