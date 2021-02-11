# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from graphene_django_crud import DjangoGrapheneCRUD, where_input_to_Q
import graphene
from .models import ModelTestGenerateSchemaA, ModelTestGenerateSchemaB, Person

class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

class GroupType(DjangoGrapheneCRUD):
    class Meta:
        model = Group

class ModelTestGenerateSchemaAType(DjangoGrapheneCRUD):
    class Meta:
        model = ModelTestGenerateSchemaA

class ModelTestGenerateSchemaBType(DjangoGrapheneCRUD):
    class Meta:
        model = ModelTestGenerateSchemaB
        input_extend_fields = (
            ("extend", graphene.Int()),
        )

class ModelTestGenerateSchemaBCustomMutation(graphene.Mutation):
    class Arguments:
        where = graphene.Argument(ModelTestGenerateSchemaBType.WhereInputType())
        create = graphene.Argument(ModelTestGenerateSchemaBType.CreateInputType())
        update = graphene.Argument(ModelTestGenerateSchemaBType.UpdateInputType())

    ok = graphene.Boolean()
    result = graphene.Field(ModelTestGenerateSchemaBType)

    def mutate(root, info, where, create, update):
        where_input_to_Q(where)
        return {
            "ok" : True,
            "result" : None
        }


class PersonType(DjangoGrapheneCRUD):
    class Meta:
        model = Person

class Query(graphene.ObjectType):
    user = UserType.ReadField()
    users = UserType.BatchReadField()

    group = GroupType.ReadField()
    groups = GroupType.BatchReadField()


    test_generate_schema_a = ModelTestGenerateSchemaAType.ReadField()
    test_generate_schema_as = ModelTestGenerateSchemaAType.BatchReadField()

    test_generate_schema_b = ModelTestGenerateSchemaBType.ReadField()
    test_generate_schema_bs = ModelTestGenerateSchemaBType.BatchReadField()

    person = PersonType.ReadField()
    persons = PersonType.BatchReadField()

class Mutation(graphene.ObjectType):
    user_create = UserType.CreateField()
    user_update = UserType.UpdateField()
    user_delete = UserType.DeleteField()

    group_create = GroupType.CreateField()
    group_update = GroupType.UpdateField()
    group_delete = GroupType.DeleteField()

    test_generate_schema_a_create = ModelTestGenerateSchemaAType.CreateField()
    test_generate_schema_a_update = ModelTestGenerateSchemaAType.UpdateField()
    test_generate_schema_a_delete = ModelTestGenerateSchemaAType.DeleteField()

    test_generate_schema_b_create = ModelTestGenerateSchemaBType.CreateField()
    test_generate_schema_b_update = ModelTestGenerateSchemaBType.UpdateField()
    test_generate_schema_b_delete = ModelTestGenerateSchemaBType.DeleteField()
    test_generate_schema_b_custom = ModelTestGenerateSchemaBCustomMutation.Field()

    person_create = PersonType.CreateField()
    person_update = PersonType.UpdateField()
    person_delete = PersonType.DeleteField()


class Subscription(graphene.ObjectType):
    user_created = UserType.CreatedField()
    user_updated = UserType.UpdatedField()
    user_deleted = UserType.DeletedField()

    test_generate_schema_a_created = ModelTestGenerateSchemaAType.CreatedField()
    test_generate_schema_a_updated = ModelTestGenerateSchemaAType.UpdatedField()
    test_generate_schema_a_deleted = ModelTestGenerateSchemaAType.DeletedField()

    test_generate_schema_b_created = ModelTestGenerateSchemaBType.CreatedField()
    test_generate_schema_b_updated = ModelTestGenerateSchemaBType.UpdatedField()
    test_generate_schema_b_deleted = ModelTestGenerateSchemaBType.DeletedField()

    person_created = PersonType.CreatedField()
    person_updated = PersonType.UpdatedField()
    person_deleted = PersonType.DeletedField()


schema = graphene.Schema(
    query=Query, 
    mutation=Mutation, 
    subscription=Subscription
    )