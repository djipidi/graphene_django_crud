# Changelog

All notable changes to this project will be documented in this file.

## \[Unreleased\]

### Added

- relay integration

## \[1.2.0\] - 2021-04-02

### Breaking change:

- Normalize oderByInput with the other inputs, it is no longer a list of strings
- Need to use the resolver_hints decorator for the creation of computed fields

### Changed

- Remove related_field in createNestedInput and updateNestedInput for
  ManyToOneRel, OnetoOneField and OnetoOneRel fields

### Added

- Improve sql performance with use only, select_related, prefetch_related
- Meta Parameter where_only_fields / where_exclude_fields, order_by_only_fields /
  order_by_exclude_fields
- add year, month, day, week_day parameters in the dateFilter
- add hour, minute, second parameters in the timeFilter

### Fixed

- FIX WhereInput don't use related_query_name

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
