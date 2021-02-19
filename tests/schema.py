# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from graphene_django_crud import DjangoGrapheneCRUD, where_input_to_Q
import graphene
from .models import *

class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    @classmethod
    def before_mutate(cls, root, info, instance, data):
        if "password" in data.keys():
            instance.set_password(data.pop("password"))

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


class TestFkAType(DjangoGrapheneCRUD):
    class Meta:
        model=TestFkA

class TestFkBType(DjangoGrapheneCRUD):
    class Meta:
        model=TestFkB

class TestFkCType(DjangoGrapheneCRUD):
    class Meta:
        model=TestFkC

class TestO2oAType(DjangoGrapheneCRUD):
    class Meta:
        model=TestO2oA

class TestO2oBType(DjangoGrapheneCRUD):
    class Meta:
        model=TestO2oB

class TestO2oCType(DjangoGrapheneCRUD):
    class Meta:
        model=TestO2oC

class TestM2mAType(DjangoGrapheneCRUD):
    class Meta:
        model=TestM2mA

class TestM2mBType(DjangoGrapheneCRUD):
    class Meta:
        model=TestM2mB

class TestM2mCType(DjangoGrapheneCRUD):
    class Meta:
        model=TestM2mC

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

    testFkA = TestFkAType.ReadField()
    testFkAs = TestFkAType.BatchReadField()

    testFkB = TestFkBType.ReadField()
    testFkBs = TestFkBType.BatchReadField()

    testFkC = TestFkCType.ReadField()
    testFkCs = TestFkCType.BatchReadField()

    testOtoA = TestO2oBType.ReadField()
    testOtoAs = TestO2oBType.BatchReadField()

    testOtoB = TestO2oBType.ReadField()
    testOtoBs = TestO2oBType.BatchReadField()

    testOtoC = TestO2oCType.ReadField()
    testOtoCs = TestO2oCType.BatchReadField()

    testM2mA = TestM2mBType.ReadField()
    testM2mAs = TestM2mBType.BatchReadField()

    testM2mB = TestM2mBType.ReadField()
    testM2mBs = TestM2mBType.BatchReadField()

    testM2mC = TestM2mCType.ReadField()
    testM2mCs = TestM2mCType.BatchReadField()

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

    testFkA_create = TestFkAType.CreateField()
    testFkA_update = TestFkAType.UpdateField()
    testFkA_delete = TestFkAType.DeleteField()

    testFkB_create = TestFkBType.CreateField()
    testFkB_update = TestFkBType.UpdateField()
    testFkB_delete = TestFkBType.DeleteField()

    testFkC_create = TestFkCType.CreateField()
    testFkC_update = TestFkCType.UpdateField()
    testFkC_delete = TestFkCType.DeleteField()

    testO2oA_create = TestO2oAType.CreateField()
    testO2oA_update = TestO2oAType.UpdateField()
    testO2oA_delete = TestO2oAType.DeleteField()

    testO2oB_create = TestO2oBType.CreateField()
    testO2oB_update = TestO2oBType.UpdateField()
    testO2oB_delete = TestO2oBType.DeleteField()

    testO2oC_create = TestO2oCType.CreateField()
    testO2oC_update = TestO2oCType.UpdateField()
    testO2oC_delete = TestO2oCType.DeleteField()

    testM2mA_create = TestM2mAType.CreateField()
    testM2mA_update = TestM2mAType.UpdateField()
    testM2mA_delete = TestM2mAType.DeleteField()

    testM2mB_create = TestM2mBType.CreateField()
    testM2mB_update = TestM2mBType.UpdateField()
    testM2mB_delete = TestM2mBType.DeleteField()

    testM2mC_create = TestM2mCType.CreateField()
    testM2mC_update = TestM2mCType.UpdateField()
    testM2mC_delete = TestM2mCType.DeleteField()

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