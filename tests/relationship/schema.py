# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoGrapheneCRUD
import graphene
from .models import *


class TestFkAType(DjangoGrapheneCRUD):
    class Meta:
        model = TestFkA


class TestFkBType(DjangoGrapheneCRUD):
    class Meta:
        model = TestFkB


class TestFkCType(DjangoGrapheneCRUD):
    class Meta:
        model = TestFkC


class TestO2oAType(DjangoGrapheneCRUD):
    class Meta:
        model = TestO2oA


class TestO2oBType(DjangoGrapheneCRUD):
    class Meta:
        model = TestO2oB


class TestO2oCType(DjangoGrapheneCRUD):
    class Meta:
        model = TestO2oC


class TestM2mAType(DjangoGrapheneCRUD):
    class Meta:
        model = TestM2mA


class TestM2mBType(DjangoGrapheneCRUD):
    class Meta:
        model = TestM2mB


class TestM2mCType(DjangoGrapheneCRUD):
    class Meta:
        model = TestM2mC


class PersonType(DjangoGrapheneCRUD):
    class Meta:
        model = Person


class Query(graphene.ObjectType):

    testFkA = TestFkAType.ReadField()
    testFkAs = TestFkAType.BatchReadField()

    testFkB = TestFkBType.ReadField()
    testFkBs = TestFkBType.BatchReadField()

    testFkC = TestFkCType.ReadField()
    testFkCs = TestFkCType.BatchReadField()

    testOtoA = TestO2oBType.ReadField()
    testOtoAs = TestO2oBType.BatchReadField()

    testOtoB = TestO2oBType.ReadField()
    testOtoBs = TestO2oBType.BatchReadField()

    testOtoC = TestO2oCType.ReadField()
    testOtoCs = TestO2oCType.BatchReadField()

    testM2mA = TestM2mBType.ReadField()
    testM2mAs = TestM2mBType.BatchReadField()

    testM2mB = TestM2mBType.ReadField()
    testM2mBs = TestM2mBType.BatchReadField()

    testM2mC = TestM2mCType.ReadField()
    testM2mCs = TestM2mCType.BatchReadField()

    person = PersonType.ReadField()
    persons = PersonType.BatchReadField()


class Mutation(graphene.ObjectType):

    testFkA_create = TestFkAType.CreateField()
    testFkA_update = TestFkAType.UpdateField()
    testFkA_delete = TestFkAType.DeleteField()

    testFkB_create = TestFkBType.CreateField()
    testFkB_update = TestFkBType.UpdateField()
    testFkB_delete = TestFkBType.DeleteField()

    testFkC_create = TestFkCType.CreateField()
    testFkC_update = TestFkCType.UpdateField()
    testFkC_delete = TestFkCType.DeleteField()

    testO2oA_create = TestO2oAType.CreateField()
    testO2oA_update = TestO2oAType.UpdateField()
    testO2oA_delete = TestO2oAType.DeleteField()

    testO2oB_create = TestO2oBType.CreateField()
    testO2oB_update = TestO2oBType.UpdateField()
    testO2oB_delete = TestO2oBType.DeleteField()

    testO2oC_create = TestO2oCType.CreateField()
    testO2oC_update = TestO2oCType.UpdateField()
    testO2oC_delete = TestO2oCType.DeleteField()

    testM2mA_create = TestM2mAType.CreateField()
    testM2mA_update = TestM2mAType.UpdateField()
    testM2mA_delete = TestM2mAType.DeleteField()

    testM2mB_create = TestM2mBType.CreateField()
    testM2mB_update = TestM2mBType.UpdateField()
    testM2mB_delete = TestM2mBType.DeleteField()

    testM2mC_create = TestM2mCType.CreateField()
    testM2mC_update = TestM2mCType.UpdateField()
    testM2mC_delete = TestM2mCType.DeleteField()

    person_create = PersonType.CreateField()
    person_update = PersonType.UpdateField()
    person_delete = PersonType.DeleteField()


class Subscription(graphene.ObjectType):

    person_created = PersonType.CreatedField()
    person_updated = PersonType.UpdatedField()
    person_deleted = PersonType.DeletedField()
