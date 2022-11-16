# Changelog

All notable changes to this project will be documented in this file.

## \[Unreleased\]

- Upgrade dependency from graphene v2 to graphene v3

### Breaking changed

- Removed subscriptions fields
- Simplification of the schema by leaving the parent field in the nestedCreateInput
- Create mutation payload for each mutation
- Rename "idFilter" to "IDfilter"

### Added

- Nested updates [#7](https://github.com/djipidi/graphene_django_crud/issues/7)
- create_only_fields, create_exclude_fields, create_extend_fields options in
  DjangoCRUDObjectType
- update_only_fields, update_exclude_fields, update_extend_fields options in
  DjangoCRUDObjectType
- create_mutation, update_mutation, delete_mutation options in
  DjangoCRUDObjectType to enable/disable nested mutation
  [#10](https://github.com/djipidi/graphene_django_crud/issues/10)
- OrderStringEnum has state sensitive or case insensitive


## \[1.3.4\] - 2022-02-11

### Fixed

- Cryptic "not found" error if result not present in GraphQL
  [#8](https://github.com/djipidi/graphene_django_crud/issues/8)

## \[1.3.3\] - 2022-01-18

### Added

- add a setting that enables / disables converting fields with choices to enum
  fields

## \[1.3.2\] - 2021-10-04

### Fixed

- Field Model.field cannot be both deferred and traversed using select_related
  at the same time
  [#5](https://github.com/djipidi/graphene_django_crud/issues/5)

## \[1.3.1\] - 2021-08-15

### Fixed

- Allow subclass of DjangoCRUDObjectType
  [#3](https://github.com/djipidi/graphene_django_crud/issues/3)

## \[1.3.0\] - 2021-06-21

### Breaking changed

- Rename "equals" field in scalar filters to "exact", the
  SCALAR_FILTERS_ADD_EQUALS_FIELD setting params restores the field.
- Boolean filter is like scalar filters, the BOOLEAN_FILTER_USE_BOOLEAN_FIELD
  setting params restore Boolean field.

### Deprecation

- DjangoGrapheneCRUD class has been renamed to DjangoCRUDObjectType, so the name
  "DjangoGrapheneCRUD" is deprecated.
- The methods before_xxx, after_xxx are deprecated. Use the methods mutate,
  create, update, delete

### Added

- Customization with django settings parameters
- Relay integration
- Possibility to extend connectionType
- Possibility of having a list field instead of a connection field
- Meta parameters for model validation
- FileField and ImageField support
- DEFAULT_CONNECTION_NODES_FIELD_NAME setting parameter for customizing the node
  field name in the default connection field
- FILE_TYPE_CONTENT_FIELD_ACTIVE setting parameter for activate/deactivate the
  content field in file type
- Add Case insensitive fields in StringFilter
- Add UUIDFilter

### Changed

- Graphql type <typeName>NodeType is renamed to <typeName>Connection
- Graphql type <typeName>MutationType is renamed to <typeName>Mutation
- String ordering is Case insensitive
- OrderEnum for string ordering rename to orderStringEnum
- Remove ordering with many Relation

## \[1.2.2\] - 2021-05-27

### Changed

- Support multiple databases by dropping the transaction in mutations resolvers

## \[1.2.1\] - 2021-05-07

### Fixed

- FIX delete field and disconnect field do not exist in updateNestedInput

## \[1.2.0\] - 2021-04-02

### Breaking change:

- Normalize oderByInput with the other inputs, it is no longer a list of strings
- Need to use the resolver_hints decorator for the creation of computed fields

### Changed

- Remove related_field in createNestedInput and updateNestedInput for
  ManyToOneRel, OnetoOneField and OnetoOneRel fields

### Added

- Improve sql performance with use only, select_related, prefetch_related
- Meta Parameter where_only_fields / where_exclude_fields, order_by_only_fields
  / order_by_exclude_fields
- add year, month, day, week_day parameters in the dateFilter
- add hour, minute, second parameters in the timeFilter

### Fixed

- FIX WhereInput does not use related_query_name

## \[1.1.1\] - 2021-03-15

### Fixed

- FIX mutation errors are used by all exceptions without processing error
  messages, now only ValidationError with message processing
- FIX a complex query can return several same instance
- FIX the createdField does not apply where input

## \[1.1.0\] - 2021-02-24

### Changed

- "WhereWithOperatorsInput" merge to "WhereInput" and keep operators
- Upgrade graphene-django dependency version to >= 2.8.0

### Added

- Add django dependency to version >= 2.2
- Add getters 'WhereInputType', 'CreateInputType', UpdateInputType from
  'GrapheneDjangoCrud' object
- Add possibility to extend the create and update input fields
- Add max_limit meta parameter for limit batchread request

### Fixed

- Improve the stability of the relationship mutations

## \[1.0.3\] - 2021-02-04

### Changed

- Replace all "WhereUniqueInput" to "WhereInput"

### Added

- Add "isnull" arg in "InputTypeFilter"

### Fixed

- FIX error mutation with related foreign key
- FIX manytomanyfield dont have BatchReadField args
- FIX bad attribute for the related field whose related_name is not specified
- FIX error in mutation resolver with foreignKeyField not null
- FIX "InputTypeFilter" of FloatField, Datefield and TimeField is not generated

## \[1.0.2\] - 2021-01-20

### Fixed

- FIX do not apply the default ordering in batchread query
- FIX do not apply the filter of the get_queryset method in the nested batchread
  query
- FIX "where" argument of ReadField is not required

## \[1.0.1\] - 2021-01-12

### Added

- GrapheneDjangoCrud class to transform django model to graphene type with crud
  field
