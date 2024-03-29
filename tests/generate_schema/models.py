# -*- coding: utf-8 -*-
from django.db import models


class ModelTestGenerateSchemaA(models.Model):

    binary_field = models.BinaryField()
    boolean_field = models.BooleanField()
    boolean_field_nullable = models.BooleanField(null=True, blank=True)
    null_boolean_field = models.NullBooleanField()
    char_field = models.CharField(max_length=100)
    char_field_unique = models.CharField(max_length=100, unique=True)
    char_field_nullable = models.CharField(max_length=100, null=True, blank=True)
    date_field = models.DateField()
    datetime_field = models.DateTimeField()
    time_field = models.TimeField()
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    duration_field = models.DurationField()
    email_field = models.EmailField()
    float_field = models.FloatField()
    integer_field = models.IntegerField()
    integer_field_unique = models.IntegerField(unique=True)
    small_integer_field = models.SmallIntegerField()
    small_integer_field_unique = models.SmallIntegerField(unique=True)
    positive_integer_field = models.PositiveIntegerField()
    positive_integer_field_unique = models.PositiveIntegerField(unique=True)
    # positive_big_integer_field = models.PositiveBigIntegerField()
    # positive_big_integer_field_unique = models.PositiveBigIntegerField(unique=True)
    # positive_small_integer_field = models.PositiveSmallIntegerField()
    # positive_small_integer_field_unique = models.PositiveSmallIntegerField(unique=True)
    slug_field = models.SlugField()
    slug_field_unique = models.SlugField(unique=True)
    text_field = models.TextField()
    text_field_nullable = models.TextField(null=True, blank=True)
    url_field = models.URLField()
    url_field_unique = models.URLField(unique=True)
    uuid_field = models.UUIDField()
    uuid_field_unique = models.UUIDField(unique=True)
    foreign_key_field = models.ForeignKey(
        "ModelTestGenerateSchemaA",
        on_delete=models.CASCADE,
        related_name="foreign_key_related",
    )
    one_to_one_field = models.OneToOneField(
        "ModelTestGenerateSchemaA",
        on_delete=models.CASCADE,
        related_name="one_to_one_related",
    )
    manytomany_field = models.ManyToManyField(
        "ModelTestGenerateSchemaA", related_name="many_to_many_related"
    )


class ModelTestGenerateSchemaB(models.Model):
    foreign_key_field = models.ForeignKey(
        "ModelTestGenerateSchemaA",
        on_delete=models.CASCADE,
        related_name="foreign_key_B_related",
    )
    one_to_one_field = models.OneToOneField(
        "ModelTestGenerateSchemaA",
        on_delete=models.CASCADE,
        related_name="one_to_one_B_related",
    )
    manytomany_field = models.ManyToManyField(
        "ModelTestGenerateSchemaA", related_name="many_to_many_B_related"
    )


class ModelTestGenerateSchemaC(models.Model):
    create_update_only = models.CharField(max_length=5)
    create_only = models.CharField(max_length=5)
    update_only = models.CharField(max_length=5)
    where_only = models.CharField(max_length=5)
    order_by_only = models.CharField(max_length=5)
    all_input = models.CharField(max_length=5)
    all_exclude = models.CharField(max_length=5)


class ModelTestGenerateSchemaD(models.Model):
    create_update_only = models.CharField(max_length=5)
    create_only = models.CharField(max_length=5)
    update_only = models.CharField(max_length=5)
    where_only = models.CharField(max_length=5)
    order_by_only = models.CharField(max_length=5)
    all_input = models.CharField(max_length=5)
    all_exclude = models.CharField(max_length=5)

class ModelTestGenerateSchemaE(models.Model):
    fk_f = models.ForeignKey("ModelTestGenerateSchemaF", on_delete=models.CASCADE, related_name="fk_f_related")
    oto_f = models.OneToOneField("ModelTestGenerateSchemaF", on_delete=models.CASCADE, related_name="oto_f_related")
    mtm_f = models.ManyToManyField("ModelTestGenerateSchemaF", related_name="mtm_f_related")
    text = models.CharField(max_length=50)

class ModelTestGenerateSchemaF(models.Model):
    text = models.CharField(max_length=50)


