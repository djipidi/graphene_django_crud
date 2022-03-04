# -*- coding: utf-8 -*-
import graphene
from .relationship.schema import (
    Query as relationshipQuery,
    Mutation as relationshipMutation,
)
from .djangocontribauth.schema import (
    Query as djangocontribauthQuery,
    Mutation as djangocontribauthMutation,
)
from .generate_schema.schema import (
    Query as generateSchemaQuery,
    Mutation as generateSchemaMutation,
)
from .choices_converter.schema import (
    Query as choicesConverterQuery,
    Mutation as choicesConverterMutation,
)
from .relay.schema import (
    Query as relayQuery,
    Mutation as relayMutation,
)
from .connection.schema import (
    Query as connectionQuery,
    Mutation as connectionMutation,
)

from .file_field.schema import (
    Query as fileFieldQuery,
    Mutation as fileFieldMutation,
)

from .issues.schema import (
    Query as issuesQuery,
    Mutation as issuesMutation,
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


schema = graphene.Schema(query=Query, mutation=Mutation)
schema_no_camelcase = graphene.Schema(
    query=Query, mutation=Mutation, auto_camelcase=False
)
