# Changelog

All notable changes to this project will be documented in this file.
## [Unreleased]

### Changed

- Replace all "WhereUniqueInput" to "WhereInput"

### Added

- Add "isnull" arg in "InputTypeFilter"

### Fixed

- FIX error mutation with related foreign key
- FIX manytomanyfield dont have BatchReadField args
- FIX bad attribute for the related field whose related_name is not specified
- FIX error in mutation resolver with foreignKeyField not null

## [1.0.2] - 2020-01-20

### Fixed

- FIX do not apply the default ordering in batchread query
- FIX do not apply the filter of the get_queryset method in the nested batchread query
- FIX "where" argument of ReadField is not required

## [1.0.1] - 2021-01-12

### Added
- GrapheneDjangoCrud class to transform django model to graphene type with crud field
