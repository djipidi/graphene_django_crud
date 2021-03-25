# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from graphene_django_crud import DjangoGrapheneCRUD, where_input_to_Q, resolver_hints
import graphene


class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    full_name = graphene.String()

    @resolver_hints(only=["first_name", "last_name"])
    @staticmethod
    def resolve_full_name(parent, info, **kwargs):
        return parent.get_full_name()

    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        if "password" in data.keys():
            instance.set_password(data.pop("password"))


class GroupType(DjangoGrapheneCRUD):
    class Meta:
        model = Group


class Query(graphene.ObjectType):
    user = UserType.ReadField()
    users = UserType.BatchReadField()

    group = GroupType.ReadField()
    groups = GroupType.BatchReadField()


class Mutation(graphene.ObjectType):
    user_create = UserType.CreateField()
    user_update = UserType.UpdateField()
    user_delete = UserType.DeleteField()

    group_create = GroupType.CreateField()
    group_update = GroupType.UpdateField()
    group_delete = GroupType.DeleteField()


class Subscription(graphene.ObjectType):
    user_created = UserType.CreatedField()
    user_updated = UserType.UpdatedField()
    user_deleted = UserType.DeletedField()

    group_created = GroupType.CreatedField()
    group_updated = GroupType.UpdatedField()
    group_deleted = GroupType.DeletedField()
