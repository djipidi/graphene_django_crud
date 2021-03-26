# -*- coding: utf-8 -*-
from django.db import models

str_choices = [
    ("a", "A"),
    ("b", "B"),
    ("c", "C"),
    ("d", "D"),
    ("e", "E"),
]

int_choices = [
    (1, "a"),
    (2, "b"),
    (3, "c"),
    (4, "d"),
    (5, "e"),
]


class TestEnumA(models.Model):
    str_enum = models.CharField(
        max_length=2,
        choices=str_choices,
        default="a",
    )
    int_enum = models.IntegerField(
        choices=int_choices,
        default=1,
    )
