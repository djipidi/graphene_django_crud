# -*- coding: utf-8 -*-
from django.db import connection
from graphene_django_crud import DjangoCRUDObjectType, DefaultConnection
import graphene
from graphene import relay
from .models import *
from django.db.models import Avg


class ConnectionWithNbAVG(DefaultConnection):
    class Meta:
        abstract = True

    nb_avg = graphene.Float()

    def resolve_nb_avg(self, info):
        return self.iterable.aggregate(Avg("nb"))["nb__avg"]


class RelayConnectionWithNbAVG(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    nb_avg = graphene.Float()

    def resolve_nb_avg(self, info):
        return self.iterable.aggregate(Avg("nb"))["nb__avg"]

    def resolve_total_count(self, info):
        return self.iterable.count()


class TestConnAType(DjangoCRUDObjectType):
    class Meta:
        model = TestConnA
        connection_class = ConnectionWithNbAVG


class TestConnBType(DjangoCRUDObjectType):
    class Meta:
        model = TestConnB
        interfaces = (relay.Node,)
        connection_class = RelayConnectionWithNbAVG


class TestConnCType(DjangoCRUDObjectType):
    class Meta:
        model = TestConnC
        use_connection = False


class Query(graphene.ObjectType):

    test_conn_a = TestConnAType.ReadField()
    test_conn_as = TestConnAType.BatchReadField()

    test_conn_b = TestConnBType.ReadField()
    test_conn_bs = TestConnBType.BatchReadField()

    test_conn_c = TestConnCType.ReadField()
    test_conn_cs = TestConnCType.BatchReadField()


class Mutation(graphene.ObjectType):

    test_conn_a_create = TestConnAType.CreateField()
    test_conn_a_update = TestConnAType.UpdateField()
    test_conn_a_delete = TestConnAType.DeleteField()

    test_conn_b_create = TestConnBType.CreateField()
    test_conn_b_update = TestConnBType.UpdateField()
    test_conn_b_delete = TestConnBType.DeleteField()

    test_conn_c_create = TestConnCType.CreateField()
    test_conn_c_update = TestConnCType.UpdateField()
    test_conn_c_delete = TestConnCType.DeleteField()


class Subscription(graphene.ObjectType):

    test_conn_a_created = TestConnAType.CreatedField()
    test_conn_a_updated = TestConnAType.UpdatedField()
    test_conn_a_deleted = TestConnAType.DeletedField()

    test_conn_b_created = TestConnBType.CreatedField()
    test_conn_b_updated = TestConnBType.UpdatedField()
    test_conn_b_deleted = TestConnBType.DeletedField()

    test_conn_c_created = TestConnCType.CreatedField()
    test_conn_c_updated = TestConnCType.UpdatedField()
    test_conn_c_deleted = TestConnCType.DeletedField()
