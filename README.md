# Graphene-Django-Crud

Inspired by prisma-nexus and graphene-django-extras, this package transforms the
django orm into a graphql API with the following features:

- Expose CRUD opérations
- Optimized queryset
- Filtering with logical operators
- Possibility to include authentication and permissions
- Nested mutations
- Subscription fields

## Table of contents

- [Graphene-Django-Crud](#graphene-django-crud)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
    - [With pip](#with-pip)
    - [With source code](#with-source-code)
  - [Usage](#usage)
    - [Example](#example)
    - [Computed Field](#computed-field)
    - [User permissions](#user-permissions)
    - [Filtering by user](#filtering-by-user)
  - [GrapheneDjangoCrud Class](#graphenedjangocrud-class)
    - [Meta parameters](#meta-parameters)
      - [model (required parameter)](#model-required-parameter)
      - [max_limit](#max_limit)
      - [only_fields / exclude_fields](#only_fields--exclude_fields)
      - [input_only_fields / input_exclude_fields](#input_only_fields--input_exclude_fields)
      - [input_extend_fields](#input_extend_fields)
      - [where_only_fields / where_exclude_fields](#where_only_fields--where_exclude_fields)
      - [order_by_only_fields / order_by_exclude_fields](#order_by_only_fields--order_by_exclude_fields)
    - [Fields](#fields)
      - [ReadField](#readfield)
      - [BatchReadField](#batchreadfield)
      - [CreateField](#createfield)
      - [UpdateField](#updatefield)
      - [DeleteField](#deletefield)
      - [CreatedField](#createdfield)
      - [UpdatedField](#updatedfield)
      - [DeletedField](#deletedfield)
    - [Input Types](#input-types)
      - [WhereInputType](#whereinputtype)
      - [OrderByInputType](#orderbyinputtype)
      - [CreateInputType](#createinputtype)
      - [UpdateInputType](#updateinputtype)
    - [overload methods](#overload-methods)
      - [get_queryset(cls, parent, info, \*\*kwargs)](#get_querysetcls-parent-info-kwargs)
      - [Middleware methods before_XXX(cls, parent, info, instance, data) / after_XXX(cls, parent, info, instance, data)](#middleware-methods-before_xxxcls-parent-info-instance-data--after_xxxcls-parent-info-instance-data)
    - [generate_signals()](#generate_signals)
  - [Utils](#utils)
      - [@resolver_hints(only: list\[str\], select_related:list\[str\])](#resolver_hintsonly-liststr-select_relatedliststr)
      - [where_input_to_Q(where_input: dict) -> Q](#where_input_to_qwhere_input-dict---q)
      - [order_by_input_to_args(order_by_input: list\[dict\]) -> list\[str\]](#order_by_input_to_argsorder_by_input-listdict---liststr)
  - [Scalar Filter](#scalar-filter)

## Installation

> For the use of the subscription fields you must have correctly installed
> graphene-subscription in your project.
> [For that follow their installation part](https://github.com/jaydenwindle/graphene-subscriptions)\
> [The generate signals](#generate_signals)
> method allows to connect model signals to graphene-subcription signals

### With pip

To install graphene-django-crud, simply run this simple command in your terminal
of choice:

```
$ pip install graphene-django-crud
```

### With source code

graphene-django-crud is developed on GitHub, You can either clone the public
repository:

```
$ git clone https://github.com/djipidi/graphene_django_crud.git
```

Once you have a copy of the source, you can embed it in your own Python package,
or install it into your site-packages easily:

```
$ cd graphene_django_crud
$ python setup.py install
```

## Usage

The GrapheneDjangoCrud class project a django model into a graphene type. The
type also has fields to exposes the CRUD operations.

### Example

In this example, you will be able to project the auth django models on your
GraphQL API and expose the CRUD operations.

```python
# schema.py
import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints

class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User
        exclude_fields = ("password",)
        input_exclude_fields = ("last_login", "date_joined")

    full_name = graphene.String()


    @resolver_hints(
      only=["first_name", "last_name"]
    )
    @staticmethod
    def resolve_full_name(parent, info, **kwargs):
        return parent.get_full_name()

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        if info.context.user.is_authenticated:
            return User.objects.all()
        else:
            return User.objects.none() 

    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        if not info.context.user.is_staff:
            raise GraphQLError('not permited, only staff user')

        if "password" in data.keys():
            instance.set_password(data.pop("password"))

class GroupType(DjangoGrapheneCRUD):
    class Meta:
        model = Group

class Query(graphene.ObjectType):

    me = graphene.Field(UserType)
    user = UserType.ReadField()
    users = UserType.BatchReadField()

    group = GroupType.ReadField()
    groups = GroupType.BatchReadField()

    def resolve_me(parent, info, **kwargs):
        if not info.context.user.is_authenticated:
            return None
        else:
            return info.context.user

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

#signals.py
from .schema import UserType, GroupType

# Necessary for subscription fields
UserType.generate_signals()
GroupType.generate_signals()
```

And get the resulting GraphQL API:

<details>
  <summary>toggle me</summary>

```gql
schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}

scalar DateTime

input DatetimeFilter {
  equals: DateTime
  in: [DateTime]
  isnull: Boolean
  gt: DateTime
  gte: DateTime
  lt: DateTime
  lte: DateTime
  year: IntFilter
  month: IntFilter
  day: IntFilter
  weekDay: IntFilter
  hour: IntFilter
  minute: IntFilter
  second: IntFilter
}

type ErrorType {
  field: String!
  messages: [String!]!
}

input GroupCreateInput {
  name: String!
  userSet: UserCreateNestedManyInput
}

input GroupCreateNestedManyInput {
  create: [GroupCreateInput]
  connect: [GroupWhereInput]
}

type GroupMutationType {
  ok: Boolean
  errors: [ErrorType]
  result: GroupType
}

type GroupNodeType {
  count: Int
  data: [GroupType]
}

input GroupOrderByInput {
  id: OrderEnum
  name: OrderEnum
  user: UserOrderByInput
}

type GroupType {
  id: ID!
  name: String
  userSet(where: UserWhereInput, limit: Int, offset: Int, orderBy: [UserOrderByInput]): UserNodeType!
}

input GroupUpdateInput {
  name: String
  userSet: UserUpdateNestedManyInput
}

input GroupUpdateNestedManyInput {
  create: [GroupCreateInput]
  delete: [GroupWhereInput]
  connect: [GroupWhereInput]
  disconnect: [GroupWhereInput]
}

input GroupWhereInput {
  id: IntFilter
  name: StringFilter
  user: UserWhereInput
  OR: [GroupWhereInput]
  AND: [GroupWhereInput]
  NOT: GroupWhereInput
}

input IntFilter {
  equals: Int
  in: [Int]
  isnull: Boolean
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
  userUpdate(input: UserUpdateInput!, where: UserWhereInput!): UserMutationType
  userDelete(where: UserWhereInput!): UserMutationType
  groupCreate(input: GroupCreateInput!): GroupMutationType
  groupUpdate(input: GroupUpdateInput!, where: GroupWhereInput!): GroupMutationType
  groupDelete(where: GroupWhereInput!): GroupMutationType
}

enum OrderEnum {
  ASC
  DESC
}

type Query {
  me: UserType
  user(where: UserWhereInput!): UserType
  users(where: UserWhereInput, limit: Int, offset: Int, orderBy: [UserOrderByInput]): UserNodeType
  group(where: GroupWhereInput!): GroupType
  groups(where: GroupWhereInput, limit: Int, offset: Int, orderBy: [GroupOrderByInput]): GroupNodeType
}

input StringFilter {
  equals: String
  in: [String]
  isnull: Boolean
  contains: String
  startswith: String
  endswith: String
  regex: String
}

type Subscription {
  userCreated(where: UserWhereInput): UserType
  userUpdated(where: UserWhereInput): UserType
  userDeleted(where: UserWhereInput): UserType
  groupCreated(where: GroupWhereInput): GroupType
  groupUpdated(where: GroupWhereInput): GroupType
  groupDeleted(where: GroupWhereInput): GroupType
}

input UserCreateInput {
  email: String
  firstName: String
  groups: GroupCreateNestedManyInput
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean
  lastName: String
  password: String!
  username: String!
}

input UserCreateNestedManyInput {
  create: [UserCreateInput]
  connect: [UserWhereInput]
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

input UserOrderByInput {
  dateJoined: OrderEnum
  email: OrderEnum
  firstName: OrderEnum
  groups: GroupOrderByInput
  id: OrderEnum
  isActive: OrderEnum
  isStaff: OrderEnum
  isSuperuser: OrderEnum
  lastLogin: OrderEnum
  lastName: OrderEnum
  username: OrderEnum
}

type UserType {
  dateJoined: DateTime
  email: String
  firstName: String
  groups(where: GroupWhereInput, limit: Int, offset: Int, orderBy: [GroupOrderByInput]): GroupNodeType!
  id: ID!
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean
  lastLogin: DateTime
  lastName: String
  username: String
  fullName: String
}

input UserUpdateInput {
  email: String
  firstName: String
  groups: GroupUpdateNestedManyInput
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean
  lastName: String
  password: String
  username: String
}

input UserUpdateNestedManyInput {
  create: [UserCreateInput]
  delete: [UserWhereInput]
  connect: [UserWhereInput]
  disconnect: [UserWhereInput]
}

input UserWhereInput {
  dateJoined: DatetimeFilter
  email: StringFilter
  firstName: StringFilter
  groups: GroupWhereInput
  id: IntFilter
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean
  lastLogin: DatetimeFilter
  lastName: StringFilter
  username: StringFilter
  OR: [UserWhereInput]
  AND: [UserWhereInput]
  NOT: UserWhereInput
}

```

</details> 

Queries example:

```gql

query{
  user(where: {id: {equals:1}}){
    id
    username
    firstName
    lastName
  }
}


query{
  users(
    where: {
      OR: [
        {isStaff: true},
        {isSuperuser: true},
        {groups: {name: {equals: "admin"}}},
      ]
    }
    orderBy: [{username: ASC}],
    limit: 100,
    offset: 0
  ){
    count
    data{
      id
      username
      firstName
      lastName
      groups{
        count
        data{
          id
          name
        }
      }
    }
  }
}

mutation{
  groupCreate(
    input: {
      name: "admin",
      userSet: {
        create: [
          {username: "woody", password: "raC4RjDU"},
        ],
        connect: [
          {id: {equals: 1}}
        ]
      },
    }
  ){
    ok
    result{
      id
      name
      userSet{
        count
        data{
          id
          username
        }
      }
    }
  }
}

```

### Computed Field

You can add computed fields using the standard Graphene API. However to optimize
the SQL query you must specify "only", "select_related" necessary for the
resolver using the resolver_hints decorator

```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    full_name = graphene.String()

    @resolver_hints(
      only=["first_name", "last_name"]
    )
    @staticmethod
    def resolve_full_name(parent, info, **kwargs):
        return parent.get_full_name()
```

### User permissions

[The Middleware methods](#middleware-methods-before_xxxcls-parent-info-instance-data--after_xxxcls-parent-info-instance-data)
are called for each modification of model instances during mutations and nested
mutations. it can be used to check permissions.

```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    @classmethod
    def before_create(cls, parent, info, instance, data):
        if not info.context.user.has_perm("add_user"):
            raise GraphQLError('not authorized, you must have add_user permission')

    @classmethod
    def before_update(cls, parent, info, instance, data):
        if not info.context.user.has_perm("change_user"):
            raise GraphQLError('not authorized, you must have change_user permission')

    @classmethod
    def before_delete(cls, parent, info, instance, data):
        if not info.context.user.has_perm("delete_user"):
            raise GraphQLError('not authorized, you must have delete_user permission')

```

### Filtering by user

To respond to several use cases, it is necessary to filter the logged in user.
the graphene module gives access to the user from the context object in info
arg. The "get_queryset" method which returns by default \<model>.objects.all(),
but it can be overloaded.

```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        if info.context.user.is_authenticated:
            return User.objects.all()
        else:
            return User.objects.none()
```

## GrapheneDjangoCrud Class

### Meta parameters

#### model (required parameter)

The model used for the definition type

#### max_limit

default : None\
To avoid too large transfers, the max_limit parameter imposes a
maximum number of return items for batchreadField and nodeField. it imposes to
use pagination. If the value is None there is no limit.

#### only_fields / exclude_fields

Tuple of model fields to include/exclude in graphql type. Only one of the two
parameters can be declared.

#### input_only_fields / input_exclude_fields

Tuple of model fields to include/exclude in graphql create and update inputs
type. Only one of the two parameters can be declared.

#### input_extend_fields

Field list to extend the create and update inputs. value must be a list of tuple
(name: string, type: graphene.ObjectType) The parameter can be processed in the
middleware functions (before_XXX / after_XXX).

example:

```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User
        input_extend_fields = (
            ("fullName", graphene.String()),
        )

    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        if "fullName" in data.keys():
            instance.first_name = data["fullName"].split(" ")[0]
            instance.last_name = data["fullName"].split(" ")[1]
        ...
```

#### where_only_fields / where_exclude_fields

Tuple of model fields to include/exclude in graphql where input type. Only one
of the two parameters can be declared.

#### order_by_only_fields / order_by_exclude_fields

Tuple of model fields to include/exclude in graphql order_by input type. Only
one of the two parameters can be declared.

### Fields

The GrapheneDjangoCrud class contains configurable operation publishers that you
use for exposing create, read, update, and delete mutations against your
projected models

for mutating, relation fields may be connected with an existing record or a
sub-create may be inlined (generally referred to as nested mutations). If the
relation is a List then multiple connections or sub-creates are permitted.

Inlined mutations are very similar to top-level ones but have the important
difference that the sub-create has excluded the field where supplying its
relation to the type of parent Object being created would normally be. This is
because a sub-create forces its record to relate to the parent one.

> **Warning**: By default, mutations are not atomic, specify ATOMIC_REQUESTS or
> ATOMIC_MUTATIONS on True in your setting.py\
> See:
> [Transaction with graphene-django](https://docs.graphene-python.org/projects/django/en/latest/mutations/#django-database-transactions)

#### ReadField

Query field to allow clients to find one particular record at time of the
respective model.

#### BatchReadField

Query field to allow clients to fetch multiple records at once of the respective
model.

#### CreateField

Mutation field to allow clients to create one record at time of the respective
model.

#### UpdateField

Mutation field to allow clients to update one particular record at time of the
respective model.

#### DeleteField

Mutation field to allow clients to delete one particular record at time of the
respective model.

#### CreatedField

Subscription field to allow customers to subscribe to the creatied of instances
of the respective model.

#### UpdatedField

Subscription field to allow customers to subscribe to the updated of instances
of the respective model.

#### DeletedField

Subscription field to allow customers to subscribe to the deleted of instances
of the respective model.

### Input Types

#### WhereInputType

Input type composed of the scalar filter of each readable fields of the model.
The logical operators "OR", "AND", "NO" are also included. the returned arg can
be used in queryset with function
[where_input_to_Q](#where_input_to_qwhere_input-dict---q)

#### OrderByInputType

Input type composed of the orderByEnum of each readable fields of the model.

#### CreateInputType

Input type composed of model fields without the id. If the field is not
nullable, the graphene field is required.

#### UpdateInputType

Input type composed of each fields of the model. No fields are required.

### overload methods

#### get_queryset(cls, parent, info, \*\*kwargs)

```python
@classmethod
def get_queryset(cls, parent, info, **kwargs):
    return queryset_class
```

Default it returns "model.objects.all()", the overload is useful for applying
filtering based on user. The method is more than a resolver, it is also called
in nested request, fetch instances for mutations and subscription filter.

#### Middleware methods before_XXX(cls, parent, info, instance, data) / after_XXX(cls, parent, info, instance, data)

```python
@classmethod
def before_mutate(cls, parent, info, instance, data):
    pass

@classmethod
def before_create(cls, parent, info, instance, data):
    pass

@classmethod
def before_update(cls, parent, info, instance, data):
    pass

@classmethod
def before_delete(cls, parent, info, instance, data):
    pass

@classmethod
def after_mutate(cls, parent, info, instance, data):
    pass

@classmethod
def after_create(cls, parent, info, instance, data):
    pass

@classmethod
def after_update(cls, parent, info, instance, data):
    pass

@classmethod
def after_delete(cls, parent, info, instance, data):
    pass
```

Methods called before or after a mutation. The "instance" argument is the
instance of the model that goes or has been modified retrieved from the "where"
argument of the mutation, or it's been created by the model constructor. The
"data" argument is a dict of the "input" argument of the mutation. The method is
also called in nested mutation.

### generate_signals()

Graphene-subscription needs to connect the model signals to its own signals. the
"generate_signals()" method does this for the model.

```python
# signals.py

from .schema import UserType, GroupTyp

UserType.generate_signals()
GroupType.generate_signals()

# apps.py

from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
```

## Utils

#### @resolver_hints(only: list\[str\], select_related:list\[str\])

Each query uses "only", "select_related" and "prefetch_related" methods of
queryset to get only the necessary attributes. To extend fields, the decorator
informs the query set builder with its arguments which model attributes are
needed to resolve the extended field.

show [Computed field](#Computed-field) section for more informations

#### where_input_to_Q(where_input: dict) -> Q

In order to be able to reuse where input generated, the where_input_to_Q
function transforms the returned argument into a Q object

example :

```python
<model>.objects.filter(where_input_to_Q(where))
```

#### order_by_input_to_args(order_by_input: list\[dict\]) -> list\[str\]

In order to be able to reuse order_by input generated, the
order_by_input_to_args function transforms the returned argument into args for
order_by method of queryset.

example :

```python
<model>.objects.all().order_by(order_by_input_to_args(where))
```

## Scalar Filter

```gql
input StringFilter {
  equals: String
  in: [String]
  isnull: Boolean
  contains: String
  startswith: String
  endswith: String
  regex: String
}

input IntFilter {
  equals: Int
  in: [Int]
  isnull: Boolean
  gt: Int
  gte: Int
  lt: Int
  lte: Int
  contains: Int
  startswith: Int
  endswith: Int
  regex: String
}

input FloatFilter {
  equals: Float
  in: [Float]
  isnull: Boolean
  gt: Float
  gte: Float
  lt: Float
  lte: Float
  contains: Float
  startswith: Float
  endswith: Float
  regex: String
}

input timeFilter {
  equals: Time
  in: [Time]
  isnull: Boolean
  gt: Time
  gte: Time
  lt: Time
  lte: Time
  hour: IntFilter
  minute: IntFilter
  second: IntFilter
}

input DateFilter {
  equals: Date
  in: [Date]
  isnull: Boolean
  gt: Date
  gte: Date
  lt: Date
  lte: Date
  year: IntFilter
  month: IntFilter
  day: IntFilter
  weekDay: IntFilter
}

input DatetimeFilter {
  equals: DateTime
  in: [DateTime]
  isnull: Boolean
  gt: DateTime
  gte: DateTime
  lt: DateTime
  lte: DateTime
  year: IntFilter
  month: IntFilter
  day: IntFilter
  weekDay: IntFilter
  hour: IntFilter
  minute: IntFilter
  second: IntFilter
}
```
