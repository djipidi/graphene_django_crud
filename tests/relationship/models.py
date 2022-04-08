# -*- coding: utf-8 -*-
from django.db import models


class TestFkA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_fk_b = models.ForeignKey(
        "TestFkB", on_delete=models.CASCADE, related_name="test_fk_as"
    )


class TestFkB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_fk_c = models.ForeignKey(
        "TestFkC", on_delete=models.SET_NULL, null=True, blank=True
    )


class TestFkC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class TestO2oA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_o2o_b = models.OneToOneField(
        "TestO2oB", on_delete=models.CASCADE, related_name="test_o2o_a"
    )

class TestO2oB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_o2o_c = models.OneToOneField(
        "TestO2oC", on_delete=models.SET_NULL, null=True, blank=True
    )

class TestO2oC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class TestM2mA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_m2m_bs = models.ManyToManyField("TestM2mB", related_name="test_m2m_as")


class TestM2mB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    test_m2m_cs = models.ManyToManyField("TestM2mC")


class TestM2mC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class Person(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    father = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="childs", null=True, blank=True
    )
    friends = models.ManyToManyField("self")
