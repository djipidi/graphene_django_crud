# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class TestGenericForeignkey(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class TestGenericRelation(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_generic_foreignkeys = GenericRelation(
        TestGenericForeignkey, related_query_name="test_generic_relation"
    )
