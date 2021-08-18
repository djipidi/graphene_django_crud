# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType
import graphene
from .models import *

from graphene import relay


class TestGenericForeignkeyType(DjangoCRUDObjectType):
    class Meta:
        model = TestGenericForeignkey


class TestGenericRelationType(DjangoCRUDObjectType):
    class Meta:
        model = TestGenericRelation


class Query(graphene.ObjectType):

    test_generic_foreignkey = TestGenericForeignkeyType.ReadField()
    test_generic_foreignkeys = TestGenericForeignkeyType.BatchReadField()

    test_generic_relation = TestGenericRelationType.ReadField()
    test_generic_relations = TestGenericRelationType.BatchReadField()


class Mutation(graphene.ObjectType):

    test_generic_foreignkey_create = TestGenericForeignkeyType.CreateField()
    test_generic_foreignkey_update = TestGenericForeignkeyType.UpdateField()
    test_generic_foreignkey_delete = TestGenericForeignkeyType.DeleteField()

    test_generic_relation_create = TestGenericRelationType.CreateField()
    test_generic_relation_update = TestGenericRelationType.UpdateField()
    test_generic_relation_delete = TestGenericRelationType.DeleteField()


class Subscription(graphene.ObjectType):

    test_generic_foreignkey_created = TestGenericForeignkeyType.CreatedField()
    test_generic_foreignkey_updated = TestGenericForeignkeyType.UpdatedField()
    test_generic_foreignkey_deleted = TestGenericForeignkeyType.DeletedField()

    test_generic_relation_created = TestGenericRelationType.CreatedField()
    test_generic_relation_updated = TestGenericRelationType.UpdatedField()
    test_generic_relation_deleted = TestGenericRelationType.DeletedField()
