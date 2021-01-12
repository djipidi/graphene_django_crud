# Graphene-Django-Crud

Inspired by prisma-nexus and graphene-django-extras, This package turns the django orm into a graphql API

## Installation

For installing graphene-django-crud, just run this command in your shell:

```
pip install graphene-django-crud
```

## Documentation:

Simple usage

```python
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
    user_update = UserType.UpdatedField()
    user_delete = UserType.DeleteField()

class Subscription(graphene.ObjectType):
    pass

schema = graphene.Schema(
    query=Query, 
    mutation=Mutation, 
    #subscription=Subscription
    )
```
<details>
  <summary>show the generated graphql schema</summary>
    ```
    schema {
    query: Query
    mutation: Mutation
    }

    scalar DateTime

    input DatetimeFilter {
    equals: DateTime
    in: [DateTime]
    gt: DateTime
    gte: DateTime
    lt: DateTime
    lte: DateTime
    }

    type ErrorType {
    field: String!
    messages: [String!]!
    }

    input IntFilter {
    equals: Int
    in: [Int]
    gt: Int
    gte: Int
    lt: Int
    lte: Int
    contains: Int
    startswith: Int
    endswith: Int
    regex: String
    }

    type Mutation {
    userCreate(input: UserCreateInput!): UserMutationType
    userUpdate(input: UserUpdateInput!, where: UserWhereUniqueInput!): UserMutationType
    userDelete(where: UserWhereUniqueInput!): UserMutationType
    }

    type Query {
    user(where: UserWhereUniqueInput): UserType
    users(where: UserWhereWithOperatorInput, limit: Int, offset: Int, orderBy: [String]): UserNodeType
    }

    input StringFilter {
    equals: String
    in: [String]
    contains: String
    startswith: String
    endswith: String
    regex: String
    }

    input UserCreateInput {
    password: String!
    lastLogin: DateTime
    isSuperuser: Boolean
    username: String!
    firstName: String
    lastName: String
    email: String
    isStaff: Boolean
    isActive: Boolean
    dateJoined: DateTime
    }

    type UserMutationType {
    ok: Boolean
    errors: [ErrorType]
    result: UserType
    }

    type UserNodeType {
    count: Int
    data: [UserType]
    }

    type UserType {
    id: ID!
    password: String
    lastLogin: DateTime
    isSuperuser: Boolean
    username: String
    firstName: String
    lastName: String
    email: String
    isStaff: Boolean
    isActive: Boolean
    dateJoined: DateTime
    }

    input UserUpdateInput {
    password: String
    lastLogin: DateTime
    isSuperuser: Boolean
    username: String
    firstName: String
    lastName: String
    email: String
    isStaff: Boolean
    isActive: Boolean
    dateJoined: DateTime
    }

    input UserWhereUniqueInput {
    id: ID
    username: String
    }

    input UserWhereWithOperatorInput {
    id: IntFilter
    password: StringFilter
    lastLogin: DatetimeFilter
    isSuperuser: Boolean
    username: StringFilter
    firstName: StringFilter
    lastName: StringFilter
    email: StringFilter
    isStaff: Boolean
    isActive: Boolean
    dateJoined: DatetimeFilter
    OR: [UserWhereWithOperatorInput]
    AND: [UserWhereWithOperatorInput]
    NOT: UserWhereWithOperatorInput
    }
    ```
</details>
