# Graphene-Django-Crud

Inspired by prisma-nexus and graphene-django-extras, This package
turns the django orm into a graphql API.

## Installation

For installing graphene-django-crud, just run this command in your shell:

```
pip install graphene-django-crud
```

## Usage

The GrapheneDjangoCrud class transforms a django model into a graphene type.
The type also has fields corresponding to the crud operation.

### Example

You will be able to project the auth django models on your GraphQL API and expose the CRUD operations.

```python
# schema.py
import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD

class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User
        exclude_fields = ("password",)
        input_exclude_fields = ("last_login", "date_joined")

    full_name = graphene.String()

    @staticmethod
    def resolve_full_name(root, info, **kwargs):
        return root.first_name + " " + root.last_name

    @classmethod
    def get_queryset(cls, root, info, **kwargs):
        if info.context.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.exclude(is_superuser=True)

    @classmethod
    def before_mutate(cls, root, info, instance, data):
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

    def resolve_me(root, info, **kwargs):
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
  gt: DateTime
  gte: DateTime
  lt: DateTime
  lte: DateTime
}

type ErrorType {
  field: String!
  messages: [String!]!
}

input GroupCreateInput {
  name: String!
  user: UserCreateNestedManyInput
}

input GroupCreateNestedManyInput {
  create: [GroupCreateInput]
  connect: [GroupWhereUniqueInput]
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

type GroupType {
  id: ID!
  name: String
  user(where: UserWhereInput, limit: Int, offset: Int, orderBy: [String]): UserNodeType!
}

input GroupUpdateInput {
  name: String
  user: UserUpdateNestedManyInput
}

input GroupUpdateNestedManyInput {
  create: [GroupCreateInput]
  remove: [GroupWhereUniqueInput]
  connect: [GroupWhereUniqueInput]
  disconnect: [GroupWhereUniqueInput]
}

input GroupWhereInput {
  id: IntFilter
  name: StringFilter
  user: UserWhereInput
}

input GroupWhereUniqueInput {
  id: ID
  name: String
}

input GroupWhereWithOperatorInput {
  id: IntFilter
  name: StringFilter
  user: UserWhereInput
  OR: [GroupWhereWithOperatorInput]
  AND: [GroupWhereWithOperatorInput]
  NOT: GroupWhereWithOperatorInput
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
  groupCreate(input: GroupCreateInput!): GroupMutationType
  groupUpdate(input: GroupUpdateInput!, where: GroupWhereUniqueInput!): GroupMutationType
  groupDelete(where: GroupWhereUniqueInput!): GroupMutationType
}

type Query {
  me: UserType
  user(where: UserWhereUniqueInput): UserType
  users(where: UserWhereWithOperatorInput, limit: Int, offset: Int, orderBy: [String]): UserNodeType
  group(where: GroupWhereUniqueInput): GroupType
  groups(where: GroupWhereWithOperatorInput, limit: Int, offset: Int, orderBy: [String]): GroupNodeType
}

input StringFilter {
  equals: String
  in: [String]
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
  connect: [UserWhereUniqueInput]
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
  dateJoined: DateTime
  email: String
  firstName: String
  groups: GroupNodeType!
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
  remove: [UserWhereUniqueInput]
  connect: [UserWhereUniqueInput]
  disconnect: [UserWhereUniqueInput]
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
}

input UserWhereUniqueInput {
  id: ID
  username: String
}

input UserWhereWithOperatorInput {
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
  OR: [UserWhereWithOperatorInput]
  AND: [UserWhereWithOperatorInput]
  NOT: UserWhereWithOperatorInput
}
```
</details>

## Filtering by user

To respond to a business logic it is necessary to filtering by user.
the graphene module gives access to the user from the context object in info arg.
The "get_queryset" method which returns by default <model>.objects.all(), but it can be overloaded.

```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User

    @classmethod
    def get_queryset(cls, root, info, **kwargs):
        if info.context.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.exclude(is_superuser=True)
```

## Fields

### ReadField
Query field with a required argument "where" that can return only an instance of
the defined type. Like the get method of the queryset. If multiple values ​​are
returned, the response will be an error.

Show doc in graphiql for more information

<details>
  <summary>show query example</summary>


```gql
query{
    <read_field_name>(where:{id:{equals:1}}){
        id
        attribute1
        attribute2
    }
}

# or

query{
    <read_field_name>(where:{<field>:{equals:1}}){
        attribute1
        attribute2
    }
}

# response

{
    "data": {
        <read_field_name>: {
            "id": 1,
            "attribute1": attribute1_value,
            "attribute2": attribute1_value
        }
    }
}
```
</details>

### BatchReadField
Query field that can return a node composed of a list items in "data" field and the total number of instances of the result in "count" field.  

Show doc in graphiql for more information

<details>
  <summary>show query example</summary>


```gql
query{
    <batch_read_field_name>(where:{id:{in:[1,2,3,4]}}){
        count
        data { 
            id
            attribute1
            attribute2
        }
    }
}

# response

{
    "data": {
        <batch_read_field_name>: {
            "count" : n
            "data": [
                {
                    "id": 1,
                    "attribute1": attribute1_value,
                    "attribute2": attribute1_value,
                },
                {
                    "id": 2,
                    "attribute1": attribute1_value,
                    "attribute2": attribute1_value,
                },
                ...
            ]
        }
    }
}
```
</details>

### CreateField
Mutation field ...

Show doc in graphiql for more information

### UpdateField
Mutation field ...

Show doc in graphiql for more information

### DeleteField
Mutation field ...

Show doc in graphiql for more information

### CreatedField
Subcription field ...

Show doc in graphiql for more information

### UpdatedField
Subcription field ...

Show doc in graphiql for more information

### DeletedField
Subcription field ...

Show doc in graphiql for more information

## Meta parameters 

### model (required parameter)
The model used for the definition type

### only_fields / exclude_fields
Tuple of model fields to include/exclude in graphql type.  
Only one of the two parameters can be declared.

### input_only_fields / input_exclude_fields
Tuple of model fields to include/exclude in graphql inputs type.
Only one of the two parameters can be declared.

### input_extend_fields
Field list to exted the create and update input. value must be a list of tuple (name: string, type: graphene.ObjectType)
the value of the field must be used and removed from dict data with the methods before_create (), before_update (), before_mutate () otherwise an TypeError exception will be raised.

example:
```python
class UserType(DjangoGrapheneCRUD):
    class Meta:
        model = User
        input_extend_fields = (
            ("fullName": graphene.String()),
        )

    @classmethod
    def before_mutate(cls, root, info, instance, data):
        if "fullName" in data.keys():
            fullName = data.pop("fullName")#remove the field to avoid having an error
        ...
```

## overload methods

### get_queryset(cls, root, info, **kwargs)
```python
@classmethod
def get_queryset(cls, root, info, **kwargs):
    return queryset_class
```
Default it returns "model.objects.all()", the overload is useful for applying filtering based on user.
The method is more than a resolver, it is also called in nested request, fetch instances for mutations and subscription verification.


### Middleware methode before_XXX(cls, root, info, instance, data) / after_XXX(cls, root, info, instance, data)
```python
@classmethod
def before_mutate(cls, root, info, instance, data):
    pass

@classmethod
def before_create(cls, root, info, instance, data):
    pass

@classmethod
def before_update(cls, root, info, instance, data):
    pass

@classmethod
def before_delete(cls, root, info, instance, data):
    pass

@classmethod
def after_mutate(cls, root, info, instance, data):
    pass

@classmethod
def after_create(cls, root, info, instance, data):
    pass

@classmethod
def after_update(cls, root, info, instance, data):
    pass

@classmethod
def after_delete(cls, root, info, instance, data):
    pass
```
Methods called before or after a mutation. The "instance" argument is the instance of the model that goes or has been modified retrieved from the "where" argument of the mutation, or it's been created by the model constructor. The "data" argument is a dict of the "input" argument of the mutation.  
The method is also called in nested mutation.



## Input Types

### WhereInputType()

Input type composed of the scalar filter of each readable fields of the model. The logical operators "or", "and", "no" are also included.
the returned arg can be used in queryset with function "where_input_to_queryset_filter_args(where)"

### CreateInputType()

Input type composed of model fields without the id. If the field is not nullable, the graphene field is required.

### UpdateInputType()

Input type composed of each fields of the model. No fields are required.

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
}

input DateFilter {
  equals: Date
  in: [Date]
  isnull: Boolean
  gt: Date
  gte: Date
  lt: Date
  lte: Date
}

input DatetimeFilter {
  equals: DateTime
  in: [DateTime]
  isnull: Boolean
  gt: DateTime
  gte: DateTime
  lt: DateTime
  lte: DateTime
}
```

## Utils

### where_input_to_Q(where_input: dict) -> Q

Function that returns the dict of the where argument to a object Q to be used in queryset.

example :

```python
<model>.objects.filter(where_input_to_Q(where))
```