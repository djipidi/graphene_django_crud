# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType
import graphene
from .models import *


class Issue8Type(DjangoCRUDObjectType):
    class Meta:
        model = Issue8

class Query(graphene.ObjectType):

    issue_8 = Issue8Type.ReadField()
    issue_8s = Issue8Type.BatchReadField()

class Mutation(graphene.ObjectType):

    issue_8_create = Issue8Type.CreateField()
    issue_8_update = Issue8Type.UpdateField()
    issue_8_delete = Issue8Type.DeleteField()


class Subscription(graphene.ObjectType):

    issue_8_created = Issue8Type.CreatedField()
    issue_8_updated = Issue8Type.UpdatedField()
    issue_8_deleted = Issue8Type.DeletedField()
