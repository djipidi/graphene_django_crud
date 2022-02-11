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
from .choices_converter.schema import (
    Query as choicesConverterQuery,
    Mutation as choicesConverterMutation,
    Subscription as choicesConverterSubscription,
)
from .relay.schema import (
    Query as relayQuery,
    Mutation as relayMutation,
    Subscription as relaySubscription,
)
from .connection.schema import (
    Query as connectionQuery,
    Mutation as connectionMutation,
    Subscription as connectionSubscription,
)

from .file_field.schema import (
    Query as fileFieldQuery,
    Mutation as fileFieldMutation,
    Subscription as fileFieldSubscription,
)

from .issues.schema import (
    Query as issuesQuery,
    Mutation as issuesMutation,
    Subscription as issuesSubscription,
)

class Query(
    relationshipQuery,
    djangocontribauthQuery,
    generateSchemaQuery,
    choicesConverterQuery,
    relayQuery,
    connectionQuery,
    fileFieldQuery,
    issuesQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    relationshipMutation,
    djangocontribauthMutation,
    generateSchemaMutation,
    choicesConverterMutation,
    relayMutation,
    connectionMutation,
    fileFieldMutation,
    issuesMutation,
    graphene.ObjectType,
):
    pass


class Subscription(
    relationshipSubscription,
    djangocontribauthSubscription,
    generateSchemaSubscription,
    choicesConverterSubscription,
    relaySubscription,
    connectionSubscription,
    fileFieldSubscription,
    issuesSubscription,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
schema_no_camelcase = graphene.Schema(
    query=Query, mutation=Mutation, subscription=Subscription, auto_camelcase=False
)
