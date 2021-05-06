# -*- coding: utf-8 -*-
from functools import partial

from django.db.models.query import QuerySet
from graphene import Int, NonNull, String, Argument
from graphene.relay import ConnectionField
from graphene.types import Field, List
from graphene_django.settings import graphene_settings
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    connection_from_list_slice,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
)
from graphene.relay import ConnectionField, PageInfo
from promise import Promise

from .base_types import node_factory_type


def related_batchread(django_type, related_field, parent, info, **kwargs):
    return django_type.batchread(parent, info, related_field=related_field, **kwargs)


class DjangoListField(Field):
    def __init__(self, _type, *args, **kwargs):

        if isinstance(_type, NonNull):
            _type = _type.of_type
        self.django_type = _type

        kwargs.setdefault("limit", Int())
        kwargs.setdefault("offset", Int())
        super(DjangoListField, self).__init__(node_factory_type(_type), *args, **kwargs)

    @property
    def type(self):
        type = super(DjangoListField, self).type
        connection_type = type
        if isinstance(type, NonNull):
            connection_type = type.of_type

        return type

        # assert issubclass(
        #     self._underlying_type, DjangoObjectType
        # ), "DjangoListField only accepts DjangoObjectType types"

    @property
    def _underlying_type(self):
        _type = self._type
        while hasattr(_type, "of_type"):
            _type = _type.of_type
        return _type

    @classmethod
    def connection_resolver(cls, resolver, max_limit, root, info, **kwargs):
        start = kwargs.get("offset", 0)
        limit = kwargs.get("limit", max_limit)
        if limit is not None and max_limit is not None:
            if limit > max_limit:
                limit = max_limit
        if limit is not None:
            end = start + limit
        else:
            end = None
        queryset = resolver(root, info, **kwargs)
        return {"iterable": queryset, "start": start, "end": end}

    def get_resolver(self, parent_resolver):
        resolver = partial(related_batchread, self.django_type, parent_resolver.args[0])
        return partial(
            self.connection_resolver,
            resolver,
            self.django_type._meta.max_limit,
        )


class DjangoConnectionField(ConnectionField):
    def __init__(self, type, *args, **kwargs):
        self.on = kwargs.pop("on", False)
        self.max_limit = kwargs.pop(
            "max_limit", graphene_settings.RELAY_CONNECTION_MAX_LIMIT
        )
        self.enforce_first_or_last = kwargs.pop(
            "enforce_first_or_last",
            graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST,
        )
        self.django_type = type
        kwargs.setdefault("offset", Int())
        super(DjangoConnectionField, self).__init__(type, *args, **kwargs)

    @property
    def type(self):

        _type = super(ConnectionField, self).type
        non_null = False
        if isinstance(_type, NonNull):
            _type = _type.of_type
            non_null = True
        # assert issubclass(
        #     _type, DjangoObjectType
        # ), "DjangoConnectionField only accepts DjangoObjectType types"
        assert _type._meta.connection, "The type {} doesn't have a connection".format(
            _type.__name__
        )
        connection_type = _type._meta.connection
        if non_null:
            return NonNull(connection_type)
        return connection_type

    @property
    def connection_type(self):
        type = self.type
        if isinstance(type, NonNull):
            return type.of_type
        return type

    @property
    def node_type(self):
        return self.connection_type._meta.node

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        # Remove the offset parameter and convert it to an after cursor.
        offset = args.pop("offset", None)
        after = args.get("after")
        if offset:
            if after:
                offset += cursor_to_offset(after) + 1
            # input offset starts at 1 while the graphene offset starts at 0
            args["after"] = offset_to_cursor(offset - 1)

        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
        else:
            list_length = len(iterable)
        list_slice_length = (
            min(max_limit, list_length) if max_limit is not None else list_length
        )

        # If after is higher than list_length, connection_from_list_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        if max_limit is not None and args.get("first", None) is None:
            if args.get("last", None) is not None:
                after = list_length - args["last"]
            else:
                args["first"] = max_limit
        connection = connection_from_list_slice(
            iterable[after:],
            args,
            slice_start=after,
            list_length=list_length,
            list_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection

    @classmethod
    def connection_resolver(
        cls, resolver, connection, max_limit, enforce_first_or_last, root, info, **args
    ):
        first = args.get("first")
        last = args.get("last")
        offset = args.get("offset")
        before = args.get("before")

        if enforce_first_or_last:
            assert first or last, (
                "You must provide a `first` or `last` value to properly paginate the `{}` connection."
            ).format(info.field_name)

        if max_limit:
            if first:
                assert first <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the `first` limit of {} records."
                ).format(first, info.field_name, max_limit)
                args["first"] = min(first, max_limit)

            if last:
                assert last <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the `last` limit of {} records."
                ).format(last, info.field_name, max_limit)
                args["last"] = min(last, max_limit)

        if offset is not None:
            assert before is None, (
                "You can't provide a `before` value at the same time as an `offset` value to properly paginate the `{}` connection."
            ).format(info.field_name)

        # eventually leads to DjangoObjectType's get_queryset (accepts queryset)
        # or a resolve_foo (does not accept queryset)
        iterable = resolver(root, info, **args)
        on_resolve = partial(
            cls.resolve_connection, connection, args, max_limit=max_limit
        )

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)

        return on_resolve(iterable)

    def get_resolver(self, parent_resolver):

        resolver = partial(related_batchread, self.django_type, parent_resolver.args[0])
        return partial(
            self.connection_resolver,
            resolver,
            self.connection_type,
            self.max_limit,
            self.enforce_first_or_last,
        )
