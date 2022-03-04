# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType, where_input_to_Q
import graphene
from .models import *


class ModelTestGenerateSchemaAType(DjangoCRUDObjectType):
    class Meta:
        model = ModelTestGenerateSchemaA


class ModelTestGenerateSchemaBType(DjangoCRUDObjectType):
    class Meta:
        model = ModelTestGenerateSchemaB
        input_extend_fields = (("extend", graphene.Int()),)


class ModelTestGenerateSchemaBCustomMutation(graphene.Mutation):
    class Arguments:
        where = graphene.Argument(ModelTestGenerateSchemaBType.WhereInputType())
        create = graphene.Argument(ModelTestGenerateSchemaBType.CreateInputType())
        update = graphene.Argument(ModelTestGenerateSchemaBType.UpdateInputType())
        where_only = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(only=("foreign_key_field",))
        )
        where_exclude = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(exclude=("foreign_key_field",))
        )
        create_only = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(only=("foreign_key_field",))
        )
        create_exclude = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(exclude=("foreign_key_field",))
        )
        update_only = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(only=("foreign_key_field",))
        )
        update_exclude = graphene.Argument(
            ModelTestGenerateSchemaBType.CreateInputType(exclude=("foreign_key_field",))
        )

    ok = graphene.Boolean()
    result = graphene.Field(ModelTestGenerateSchemaBType)

    def mutate(parent, info, where, create, update):
        where_input_to_Q(where)
        return {"ok": True, "result": None}


class Query(graphene.ObjectType):

    test_generate_schema_a = ModelTestGenerateSchemaAType.ReadField()
    test_generate_schema_as = ModelTestGenerateSchemaAType.BatchReadField()

    test_generate_schema_b = ModelTestGenerateSchemaBType.ReadField()
    test_generate_schema_bs = ModelTestGenerateSchemaBType.BatchReadField()


class Mutation(graphene.ObjectType):

    test_generate_schema_a_create = ModelTestGenerateSchemaAType.CreateField()
    test_generate_schema_a_update = ModelTestGenerateSchemaAType.UpdateField()
    test_generate_schema_a_delete = ModelTestGenerateSchemaAType.DeleteField()

    test_generate_schema_b_create = ModelTestGenerateSchemaBType.CreateField()
    test_generate_schema_b_update = ModelTestGenerateSchemaBType.UpdateField()
    test_generate_schema_b_delete = ModelTestGenerateSchemaBType.DeleteField()
    test_generate_schema_b_custom = ModelTestGenerateSchemaBCustomMutation.Field()
