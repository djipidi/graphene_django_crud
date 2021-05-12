# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType
import graphene
from .models import *


class TestEnumAType(DjangoCRUDObjectType):
    class Meta:
        model = TestEnumA


class Query(graphene.ObjectType):

    test_enum_a = TestEnumAType.ReadField()
    test_enum_as = TestEnumAType.BatchReadField()


class Mutation(graphene.ObjectType):

    test_enum_a_create = TestEnumAType.CreateField()
    test_enum_a_update = TestEnumAType.UpdateField()
    test_enum_a_delete = TestEnumAType.DeleteField()


class Subscription(graphene.ObjectType):

    test_enum_a_created = TestEnumAType.CreatedField()
    test_enum_a_updated = TestEnumAType.UpdatedField()
    test_enum_a_deleted = TestEnumAType.DeletedField()
