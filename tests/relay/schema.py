# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType
import graphene
from .models import *

from graphene import relay

class TestRelayAType(DjangoCRUDObjectType):
    class Meta:
        model = TestRelayA
        interfaces = (relay.Node, )


class TestRelayBType(DjangoCRUDObjectType):
    class Meta:
        model = TestRelayB
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):

    test_relay_a = TestRelayAType.ReadField()
    test_relay_as = TestRelayAType.BatchReadField()

    test_relay_b = TestRelayBType.ReadField()
    test_relay_bs = TestRelayBType.BatchReadField()

    node = relay.Node.Field()



class Mutation(graphene.ObjectType):

    test_relay_a_create = TestRelayAType.CreateField()
    test_relay_a_update = TestRelayAType.UpdateField()
    test_relay_a_delete = TestRelayAType.DeleteField()

    test_relay_b_create = TestRelayBType.CreateField()
    test_relay_b_update = TestRelayBType.UpdateField()
    test_relay_b_delete = TestRelayBType.DeleteField()
