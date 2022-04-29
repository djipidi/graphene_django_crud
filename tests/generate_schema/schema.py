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


class ModelTestGenerateSchemaCType(DjangoCRUDObjectType):
    class Meta:
        model = ModelTestGenerateSchemaC
        exclude_fields = ["all_exclude"]
        input_exclude_fields = ["all_exclude", "where_only", "order_by_only"]
        create_only_fields = ["create_update_only", "create_only", "all_input"]
        create_extend_fields = (("create_extend", graphene.Int()),)
        update_only_fields = ["create_update_only", "update_only", "all_input"]
        update_extend_fields = (("update_extend", graphene.Int()),)
        where_only_fields = ["where_only", "all_input"]
        order_by_only_fields = ["order_by_only", "all_input"]


class ModelTestGenerateSchemaDType(DjangoCRUDObjectType):
    class Meta:
        model = ModelTestGenerateSchemaD
        exclude_fields = ["all_exclude"]
        input_exclude_fields = ["all_exclude", "where_only", "order_by_only"]
        create_exclude_fields = ["update_only"]
        create_extend_fields = (("create_extend", graphene.Int()),)
        update_exclude_fields = ["create_only"]
        update_extend_fields = (("update_extend", graphene.Int()),)
        where_exclude_fields = [
            "order_by_only",
            "create_update_only",
            "create_only",
            "update_only",
        ]
        order_by_exclude_fields = [
            "where_only",
            "create_update_only",
            "create_only",
            "update_only",
        ]


class Query(graphene.ObjectType):

    test_generate_schema_a = ModelTestGenerateSchemaAType.ReadField()
    test_generate_schema_as = ModelTestGenerateSchemaAType.BatchReadField()

    test_generate_schema_b = ModelTestGenerateSchemaBType.ReadField()
    test_generate_schema_bs = ModelTestGenerateSchemaBType.BatchReadField()

    test_generate_schema_c = ModelTestGenerateSchemaCType.ReadField()
    test_generate_schema_cs = ModelTestGenerateSchemaCType.BatchReadField()

    test_generate_schema_d = ModelTestGenerateSchemaDType.ReadField()
    test_generate_schema_ds = ModelTestGenerateSchemaDType.BatchReadField()


class Mutation(graphene.ObjectType):

    test_generate_schema_a_create = ModelTestGenerateSchemaAType.CreateField()
    test_generate_schema_a_update = ModelTestGenerateSchemaAType.UpdateField()
    test_generate_schema_a_delete = ModelTestGenerateSchemaAType.DeleteField()

    test_generate_schema_b_create = ModelTestGenerateSchemaBType.CreateField()
    test_generate_schema_b_update = ModelTestGenerateSchemaBType.UpdateField()
    test_generate_schema_b_delete = ModelTestGenerateSchemaBType.DeleteField()
    test_generate_schema_b_custom = ModelTestGenerateSchemaBCustomMutation.Field()

    test_generate_schema_c_create = ModelTestGenerateSchemaCType.CreateField()
    test_generate_schema_c_update = ModelTestGenerateSchemaCType.UpdateField()
    test_generate_schema_c_delete = ModelTestGenerateSchemaCType.DeleteField()

    test_generate_schema_d_create = ModelTestGenerateSchemaDType.CreateField()
    test_generate_schema_d_update = ModelTestGenerateSchemaDType.UpdateField()
    test_generate_schema_d_delete = ModelTestGenerateSchemaDType.DeleteField()


class Subscription(graphene.ObjectType):

    test_generate_schema_a_created = ModelTestGenerateSchemaAType.CreatedField()
    test_generate_schema_a_updated = ModelTestGenerateSchemaAType.UpdatedField()
    test_generate_schema_a_deleted = ModelTestGenerateSchemaAType.DeletedField()

    test_generate_schema_b_created = ModelTestGenerateSchemaBType.CreatedField()
    test_generate_schema_b_updated = ModelTestGenerateSchemaBType.UpdatedField()
    test_generate_schema_b_deleted = ModelTestGenerateSchemaBType.DeletedField()

    test_generate_schema_c_created = ModelTestGenerateSchemaCType.CreatedField()
    test_generate_schema_c_updated = ModelTestGenerateSchemaCType.UpdatedField()
    test_generate_schema_c_deleted = ModelTestGenerateSchemaCType.DeletedField()

    test_generate_schema_d_created = ModelTestGenerateSchemaDType.CreatedField()
    test_generate_schema_d_updated = ModelTestGenerateSchemaDType.UpdatedField()
    test_generate_schema_d_deleted = ModelTestGenerateSchemaDType.DeletedField()
