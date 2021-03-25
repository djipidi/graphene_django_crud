# -*- coding: utf-8 -*-
import graphene
from .relationship.schema import (
    Query as relationshipQuery,
    Mutation as relationshipMutation,
    Subscription as relationshipSubscription,
)
from .djangocontribauth.schema import (
    Query as djangocontribauthQuery,
    Mutation as djangocontribauthMutation,
    Subscription as djangocontribauthSubscription,
)
from .generate_schema.schema import (
    Query as generateSchemaQuery,
    Mutation as generateSchemaMutation,
    Subscription as generateSchemaSubscription,
)


class Query(
    relationshipQuery,
    djangocontribauthQuery,
    generateSchemaQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    relationshipMutation,
    djangocontribauthMutation,
    generateSchemaMutation,
    graphene.ObjectType,
):
    pass


class Subscription(
    relationshipSubscription,
    djangocontribauthSubscription,
    generateSchemaSubscription,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
schema_no_camelcase = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription, auto_camelcase=False)
