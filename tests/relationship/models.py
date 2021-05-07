# -*- coding: utf-8 -*-
from django.db import models


class TestFkA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    testFkB = models.ForeignKey(
        "TestFkB", on_delete=models.CASCADE, related_name="testFkAs"
    )


class TestFkB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    testFkC = models.ForeignKey(
        "TestFkC", on_delete=models.CASCADE, null=True, blank=True
    )


class TestFkC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class TestO2oA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    TestO2oB = models.OneToOneField(
        "TestO2oB", on_delete=models.CASCADE, related_name="testO2oA"
    )


class TestO2oB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    TestO2oC = models.OneToOneField(
        "TestO2oC", on_delete=models.CASCADE, null=True, blank=True
    )


class TestO2oC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class TestM2mA(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    testM2mBs = models.ManyToManyField("TestM2mB", related_name="testM2mAs")


class TestM2mB(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    testM2mCs = models.ManyToManyField("TestM2mC")


class TestM2mC(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)


class Person(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    father = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="childs", null=True, blank=True
    )
    friends = models.ManyToManyField("self")
