# Graphene-Django-Crud

Inspired by prisma-nexus and graphene-django-extras, this package transforms the
django orm into a graphql API with the following features:

- Expose CRUD opérations
- Optimized queryset
- Filtering with logical operators
- Authentication and permissions
- Nested mutations
- Subscription fields

## Table of contents

- [Graphene-Django-Crud](#graphene-django-crud)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
    - [Install with pip](#install-with-pip)
    - [Install with source code](#install-with-source-code)
  - [Usage](#usage)
    - [Example](#example)
    - [Computed Field](#computed-field)
    - [User permissions](#user-permissions)
    - [Filtering by user](#filtering-by-user)
    - [Use with relay](#use-with-relay)
    - [Extend ConnectionType](#extend-connectiontype)
      - [Use list field](#use-list-field)
      - [Extend ConnectionType without Relay](#extend-connectiontype-without-relay)
      - [Extend ConnectionType with Relay](#extend-connectiontype-with-relay)
  - [DjangoCRUDObjectType Class](#djangocrudobjecttype-class)
    - [Meta parameters](#meta-parameters)
      - [model](#model)
      - [max_limit](#max_limit)
      - [only_fields / exclude_fields](#only_fields--exclude_fields)
      - [input_only_fields / input_exclude_fields](#input_only_fields--input_exclude_fields)
      - [input_extend_fields](#input_extend_fields)
      - [where_only_fields / where_exclude_fields](#where_only_fields--where_exclude_fields)
      - [order_by_only_fields / order_by_exclude_fields](#order_by_only_fields--order_by_exclude_fields)
      - [validator](#validator)
      - [validator_exclude](#validator_exclude)
      - [validator_validate_unique](#validator_validate_unique)
    - [Graphene Fields](#graphene-fields)
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
    - [Methods to override](#methods-to-override)
      - [get_queryset(cls, parent, info, \*\*kwargs)](#get_querysetcls-parent-info-kwargs)
      - [mutate, create, update, delete](#mutate-create-update-delete)
      - [(Deprecated) Middleware methods before_XXX(cls, parent, info, instance, data) / after_XXX(cls, parent, info, instance, data)](#deprecated-middleware-methods-before_xxxcls-parent-info-instance-data--after_xxxcls-parent-info-instance-data)
    - [generate_signals()](#generate_signals)
  - [Settings](#settings)
    - [Customize](#customize)
      - [DEFAULT_CONNECTION_NODES_FIELD_NAME](#default_connection_nodes_field_name)
      - [FILE_TYPE_CONTENT_FIELD_ACTIVE](#file_type_content_field_active)
      - [CONVERT_ENUM_FIELDS](#convert_enum_fields)
    - [Compatibility with old version](#compatibility-with-old-version)
      - [SCALAR_FILTERS_ADD_EQUALS_FIELD](#scalar_filters_add_equals_field)
      - [BOOLEAN_FILTER_USE_BOOLEAN_FIELD](#boolean_filter_use_boolean_field)
  - [Utils](#utils)
      - [@resolver_hints(only: list\[str\], select_related:list\[str\])](#resolver_hintsonly-liststr-select_relatedliststr)
      - [where_input_to_Q(where_input: dict) -> Q](#where_input_to_qwhere_input-dict---q)
      - [order_by_input_to_args(order_by_input: list\[dict\]) -> list\[str\]](#order_by_input_to_argsorder_by_input-listdict---liststr)
  - [Graphql types](#graphql-types)
    - [File](#file)
    - [FileInput](#fileinput)
    - [Binary](#binary)
    - [Scalar filters](#scalar-filters)

## Installation

> For the use of the subscription fields you must have correctly installed
> graphene-subscription in your project.
> [For that follow their installation part](https://github.com/jaydenwindle/graphene-subscriptions)\
> [The generate signals](#generate_signals)
> method allows to connect model signals to graphene-subcription signals.

> For the support of
> [Multipart Request Spec](https://github.com/jaydenseric/graphql-multipart-request-spec),
> install [graphene-file-upload](https://pypi.org/project/graphene-file-upload/)
> according to the documentation.

### Install with pip

To install graphene-django-crud, simply run this simple command in your terminal
of choice:

```
$ pip install graphene-django-crud
```

### Install with source code

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

The DjangoCRUDObjectType class project a django model into a graphene type. The
type has fields to exposes the CRUD operations.

### Example

In this example, you will be able to project the auth django models on your
GraphQL API and expose the CRUD operations.

```python
# schema.py
import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoCRUDObjectType, resolver_hints

class UserType(DjangoCRUDObjectType):
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
    def mutate(cls, parent, info, instance, data, *args, **kwargs):
        if not info.context.user.is_staff:
            raise GraphQLError('not permited, only staff user')

        if "password" in data.keys():
            instance.set_password(data.pop("password"))
        return super().mutate(parent, info, instance, data, *args, **kwargs)

class GroupType(DjangoCRUDObjectType):
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
  exact: DateTime
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

input GroupOrderByInput {
  id: OrderEnum
  name: OrderStringEnum
}

type GroupType {
  id: ID
  name: String
  userSet(where: UserWhereInput, orderBy: [UserOrderByInput], limit: Int, offset: Int): UserTypeConnection
}

type GroupTypeConnection {
  data: [GroupType]!
  count: Int
}

type GroupTypeMutation {
  ok: Boolean
  errors: [ErrorType]
  result: GroupType
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
  id: IdFilter
  name: StringFilter
  user: UserWhereInput
  OR: [GroupWhereInput]
  AND: [GroupWhereInput]
  NOT: GroupWhereInput
}

input IdFilter {
  equals: ID
  exact: ID
  in: [ID]
  isnull: Boolean
}

input IntFilter {
  equals: Int
  exact: Int
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
  userCreate(input: UserCreateInput!): UserTypeMutation
  userUpdate(input: UserUpdateInput!, where: UserWhereInput!): UserTypeMutation
  userDelete(where: UserWhereInput!): UserTypeMutation
  groupCreate(input: GroupCreateInput!): GroupTypeMutation
  groupUpdate(input: GroupUpdateInput!, where: GroupWhereInput!): GroupTypeMutation
  groupDelete(where: GroupWhereInput!): GroupTypeMutation
}

enum OrderEnum {
  ASC
  DESC
}

enum OrderStringEnum {
  ASC
  DESC
}

type Query {
  me: UserType
  user(where: UserWhereInput!): UserType
  users(where: UserWhereInput, orderBy: [UserOrderByInput], limit: Int, offset: Int): UserTypeConnection
  group(where: GroupWhereInput!): GroupType
  groups(where: GroupWhereInput, orderBy: [GroupOrderByInput], limit: Int, offset: Int): GroupTypeConnection
}

input StringFilter {
  equals: String
  exact: String
  in: [String]
  isnull: Boolean
  contains: String
  startswith: String
  endswith: String
  regex: String
  iexact: String
  icontains: String
  istartswith: String
  iendswith: String
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

input UserOrderByInput {
  dateJoined: OrderEnum
  email: OrderStringEnum
  firstName: OrderStringEnum
  id: OrderEnum
  isActive: OrderEnum
  isStaff: OrderEnum
  isSuperuser: OrderEnum
  lastLogin: OrderEnum
  lastName: OrderStringEnum
  username: OrderStringEnum
}

type UserType {
  id: ID
  dateJoined: DateTime
  email: String
  firstName: String
  groups(where: GroupWhereInput, orderBy: [GroupOrderByInput], limit: Int, offset: Int): GroupTypeConnection
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean
  lastLogin: DateTime
  lastName: String
  username: String
  fullName: String
}

type UserTypeConnection {
  data: [UserType]!
  count: Int
}

type UserTypeMutation {
  ok: Boolean
  errors: [ErrorType]
  result: UserType
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
  id: IdFilter
  dateJoined: DatetimeFilter
  email: StringFilter
  firstName: StringFilter
  groups: GroupWhereInput
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
class UserType(DjangoCRUDObjectType):
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

[The methods mutate, create, update, delete](#mutate-create-update-delete) are
called for each change of model instances during mutations and nested mutations.
They can be used to check permissions.

```python
class UserType(DjangoCRUDObjectType):
    class Meta:
        model = User

    @classmethod
    def mutate(cls, parent, info, instance, data, *args, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError('not authorized, you must be logged in')
        return super().mutate(parent, info, instance, data, *args, **kwargs)

    @classmethod
    def create(cls, parent, info, instance, data, *args, **kwargs):
        if not info.context.user.has_perm("add_user"):
            raise GraphQLError('not authorized, you must have add_user permission')
        return super().create(parent, info, instance, data, *args, **kwargs)

    @classmethod
    def update(cls, parent, info, instance, data, *args, **kwargs):
        if not info.context.user.has_perm("change_user"):
            raise GraphQLError('not authorized, you must have change_user permission')
        return super().update(parent, info, instance, data, *args, **kwargs)

    @classmethod
    def delete(cls, parent, info, instance, data, *args, **kwargs):
        if not info.context.user.has_perm("delete_user"):
            raise GraphQLError('not authorized, you must have delete_user permission')
        return super().delete(parent, info, instance, data, *args, **kwargs)

```

### Filtering by user

To filter based on the authenticated user, overload the get_queryset method as
the example

```python
class UserType(DjangoCRUDObjectType):
    class Meta:
        model = User

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        if info.context.user.is_authenticated:
            return User.objects.all()
        else:
            return User.objects.none()
```

### Use with relay

The configuration is the same as graphene-django, just add the "relay.Node"
interface.

```python

class CategoryType(DjangoCRUDObjectType):
    class Meta:
        model = Category
        interfaces = (relay.Node, )


class IngredientType(DjangoCRUDObjectType):
    class Meta:
        model = Ingredient
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):

    node = relay.Node.Field()

    category = CategoryType.ReadField()
    all_categories = CategoryType.BatchReadField()

    ingredient = IngredientType.ReadField()
    all_ingredients = IngredientType.BatchReadField()

```

Relay.global_id as well as model id are supported to write the query using the
"id" field of whereInputType.

### Extend ConnectionType

By default, graphene_django_crud creates a connection type for the bachread
request and the many_to_many/many_to_one relationships.

the default connection has a "count" field returning the count() value of the
queryset and a data field returning the results of the queryset.

#### Use list field

```python
from .models import Product
import graphene
from graphene_django_crud import DjangoCRUDObjectType

class ProductType(DjangoCRUDObjectType):
    class Meta:
        model = Product
        use_connection = False
```

#### Extend ConnectionType without Relay

```python
from .models import Product
from django.db.models import Avg
import graphene
from graphene_django_crud import DefaultConnection, DjangoCRUDObjectType

class ConnectionWithPriceAVG(DefaultConnection):
    class Meta:
        abstract = True

    price_avg = graphene.Float()

    def resolve_price_avg(self, info):
        return self.iterable.aggregate(Avg('price'))["price__avg"]

class ProductType(DjangoCRUDObjectType):
    class Meta:
        model = Product
        connection_class = ConnectionWithPriceAVG
```

#### Extend ConnectionType with Relay

```python
from .models import Product
import graphene
from graphene_django_crud import DjangoCRUDObjectType

class ConnectionWithTotalCount(graphene.Connection):
    class Meta:
        abstract = True
    total_count = graphene.Int()

    def resolve_total_count(self, info):
        return self.iterable.count()

class ProductType(DjangoCRUDObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node, )
        connection_class = ConnectionWithTotalCount
```

## DjangoCRUDObjectType Class

> From the version v1.3.0, `DjangoGrapheneCRUD` class has been renamed to
> `DjangoCRUDObjectType`, so the name "DjangoGrapheneCRUD" is deprecated.

### Meta parameters

#### model

Required parameter\
The model used for the definition type

#### max_limit

default : `None`\
To avoid too large transfers, the max_limit parameter imposes
a maximum number of return items for batchreadField and nodeField. it imposes to
use pagination. If the value is `None` there is no limit.

#### only_fields / exclude_fields

Tuple of model fields to include/exclude in graphql type. Only one of the two
parameters can be declared.

#### input_only_fields / input_exclude_fields

Tuple of model fields to include/exclude in graphql create and update inputs
type. Only one of the two parameters can be declared.

#### input_extend_fields

Field list to extend the create and update inputs. value must be a list of tuple
(name: string, type: graphene.ObjectType). The parameters can be processed with
methods [mutate, create, update, delete](#mutate-create-update-delete)

example:

```python
class UserType(DjangoCRUDObjectType):
    class Meta:
        model = User
        input_extend_fields = (
            ("fullName", graphene.String()),
        )

    @classmethod
    def mutate(cls, parent, info, instance, data, *args, **kwargs):
        if "fullName" in data.keys():
            instance.first_name = data["fullName"].split(" ")[0]
            instance.last_name = data["fullName"].split(" ")[1]
        return super().mutate(parent, info, instance, data, *args, **kwargs)
```

#### where_only_fields / where_exclude_fields

Tuple of model fields to include/exclude in graphql where input type. Only one
of the two parameters can be declared.

#### order_by_only_fields / order_by_exclude_fields

Tuple of model fields to include/exclude in graphql order_by input type. Only
one of the two parameters can be declared.

#### validator

default: True\
Activate/deactivate the validation of the model. if the value is
True, full_clean() method of model will be called before save().

#### validator_exclude

default: None\
The exclude argument of full_clean() method.

#### validator_validate_unique

default: True\
The validate_unique argument of full_clean() method.

### Graphene Fields

The DjangoCRUDObjectType class contains configurable operation publishers that
you use for exposing create, read, update, and delete mutations against your
projected models

for mutating, relation fields may be connected with an existing record or a
sub-create may be inlined (generally referred to as nested mutations). If the
relation is a List then multiple connections or sub-creates are permitted.

Inlined mutations are very similar to top-level ones but have the important
difference that the sub-create has excluded the field where supplying its
relation to the type of parent Object being created would normally be. This is
because a sub-create forces its record to relate to the parent one.

> **Warning**: By default, mutations are not atomic, specify `ATOMIC_REQUESTS`
> or `ATOMIC_MUTATIONS` on True in your setting.py\
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

Input type composed of [the scalar filters](#scalar-filters) of each readable
fields of the model. The logical operators "OR", "AND", "NO" are also included.
the returned arg can be used in queryset with function
[where_input_to_Q](#where_input_to_qwhere_input-dict---q)

#### OrderByInputType

Input type composed of the orderByEnum of each readable fields of the model.

#### CreateInputType

Input type composed of model fields without the id. If the field is not
nullable, the graphene field is required.

#### UpdateInputType

Input type composed of each fields of the model. No fields are required.

### Methods to override

#### get_queryset(cls, parent, info, \*\*kwargs)

```python
@classmethod
def get_queryset(cls, parent, info, **kwargs):
    return queryset_class
```

Default it returns "model.objects.all()", the overload is useful for applying
filtering based on user. The method is called in nested request, fetch instances
for mutations and subscription filter.

#### mutate, create, update, delete

Methods called for each mutation and nested mutation impacting the model.
Overload this method to add preprocessing and / or overprocessing. The mutate
method is called before the create, update, delete methods. The "data" argument
is a dict corresponding to the graphql input argument.

```python
@classmethod
def mutate(cls, parent, info, instance, data, *args, **kwargs):
    # code before save instance
    instance = super().mutate(cls, parent, info, instance, data, *args, **kwargs)
    # code after save instance
    return instance

@classmethod
def create(cls, parent, info, instance, data, *args, **kwargs):
    # code before save instance
    instance = super().create(cls, parent, info, instance, data, *args, **kwargs)
    # code after save instance
    return instance

@classmethod
def update(cls, parent, info, instance, data, *args, **kwargs):
    # code before save instance
    instance = super().update(cls, parent, info, instance, data, *args, **kwargs)
    # code after save instance
    return instance

@classmethod
def delete(cls, parent, info, instance, data, *args, **kwargs):
    # code before save instance
    instance = super().delete(cls, parent, info, instance, data, *args, **kwargs)
    # code after save instance
    return instance
```

#### (Deprecated) Middleware methods before_XXX(cls, parent, info, instance, data) / after_XXX(cls, parent, info, instance, data)

> from the version v1.3.0, these methods are deprecated, use the methods
> [mutate, create, update, delete](#mutate-create-update-delete)

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

## Settings

Graphene-django-crud reads your configuration from a single Django setting named
GRAPHENE_DJANGO_CRUD:

```python
GRAPHENE_DJANGO_CRUD = {
    "DEFAULT_CONNECTION_NODES_FIELD_NAME": "nodes"
}
```

Here’s a list of settings available in graphene-django-crud and their default
values:

### Customize

#### DEFAULT_CONNECTION_NODES_FIELD_NAME

Name of node field in connection field.\
Default: `'data'`

#### FILE_TYPE_CONTENT_FIELD_ACTIVE

Add a content field with the content of the file. The type used is
Binary.\
Default: `False`

#### CONVERT_ENUM_FIELDS

Enables / disables converting fields with choices to enum fields.\
Default: `True`

### Compatibility with old version

#### SCALAR_FILTERS_ADD_EQUALS_FIELD

From version 1.3.0 the "equals" field of all scalar filters has been renamed to
"exact". To keep the client compatible we can add it by set the parameter to
`True`.\
Default: `False`

#### BOOLEAN_FILTER_USE_BOOLEAN_FIELD

From version 1.3.0 the filter boolean is like the other scalar filters. To keep
the client compatible we can add it by set the parameter to `True`.\
Default:
`False`

## Utils

#### @resolver_hints(only: list\[str\], select_related:list\[str\])

Each query uses "only", "select_related" and "prefetch_related" methods of
queryset to get only the necessary attributes. To extend fields, the decorator
is necessary for the queryset builder with its arguments which model attributes
are needed to resolve the field.

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

## Graphql types

### File

```gql
type File {
  url: String
  size: Int
  filename: String
  content: Binary
}
```

Represents File, it's converted for models.FileField and models.ImageField. The
content field is deactivated by default, set the
[FILE_TYPE_CONTENT_FIELD_ACTIVE](#file_type_content_field_active) setting to
`True` for activate.

### FileInput

```gql
input FileInput {
  upload: Upload
  filename: String
  content: Binary
}
```

Input type used to upload the file by giving a name and the content of the file.
The upload field appears if graphene-file-upload is installed, it is used to
upload this the
[Multipart Request Spec](https://github.com/jaydenseric/graphql-multipart-request-spec).

### Binary

```gql
scalar Binary
```

Represents `Bytes` that are base64 encoded and decoded.

### Scalar filters

```gql
input StringFilter {
  equals: String
  exact: String
  in: [String]
  isnull: Boolean
  contains: String
  startswith: String
  endswith: String
  regex: String
  iexact: String
  icontains: String
  istartswith: String
  iendswith: String
}

input IntFilter {
  equals: Int
  exact: Int
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
  exact: Float
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
  exact: Time
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
  exact: Date
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
  exact: DateTime
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
