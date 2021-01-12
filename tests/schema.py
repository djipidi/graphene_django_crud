# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD
import graphene

class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

class Query(graphene.ObjectType):
    user = UserType.ReadField()
    users = UserType.BatchReadField()

class Mutation(graphene.ObjectType):
    user_create = UserType.CreateField()
    user_update = UserType.UpdateField()
    user_delete = UserType.DeleteField()

class Subscription(graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query, 
    mutation=Mutation, 
    #subscription=Subscription
    )

print(schema)