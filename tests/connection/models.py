# -*- coding: utf-8 -*-
from django.db import models


class TestConnA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    nb = models.IntegerField(null=True, blank=True)


class TestConnB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    nb = models.IntegerField(null=True, blank=True)
    test_conn_a = models.ForeignKey(
        "TestConnA",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="test_conn_bs",
    )


class TestConnC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    nb = models.IntegerField(null=True, blank=True)
    test_conn_a = models.ForeignKey(
        "TestConnA",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="test_conn_cs",
    )
