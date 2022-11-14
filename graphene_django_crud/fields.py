# -*- coding: utf-8 -*-
from functools import partial
from django.db.models import query

from django.db.models.query import QuerySet
from graphene import Int, NonNull, String, Argument
from graphene.relay import ConnectionField, Connection as relayConnection
from graphene.relay.connection import connection_adapter, page_info_adapter
from graphene.relay import ConnectionField
from graphene.types import Field, List
from graphene_django.settings import graphene_settings
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    connection_from_array_slice as connection_from_list_slice,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
)
from promise import Promise


def related_batchread(django_type, related_field, parent, info, **kwargs):
    return django_type.batchread(parent, info, related_field=related_field, **kwargs)


class DjangoListField(Field):
    def __init__(self, _type, *args, **kwargs):

        if isinstance(_type, NonNull):
            _type = _type.of_type
        self.django_type = _type

        kwargs.setdefault("limit", Int())
        kwargs.setdefault("offset", Int())
        super(DjangoListField, self).__init__(List(_type), *args, **kwargs)

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
        return queryset[start:end]

    def wrap_resolve(self, parent_resolver):
        resolver = partial(related_batchread, self.django_type, parent_resolver.args[0])
        return partial(
            self.connection_resolver,
            resolver,
            self.django_type._meta.max_limit,
        )


class DjangoConnectionField(ConnectionField):
    def __init__(self, type, *args, **kwargs):
        if issubclass(type._meta.connection, relayConnection):
            self.relay = True
            self.enforce_first_or_last = kwargs.pop(
                "enforce_first_or_last",
                graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST,
            )
        else:
            self.relay = False
            kwargs.setdefault("limit", Int())

        self.on = kwargs.pop("on", False)

        if type._meta.max_limit is not None:
            self.max_limit = type._meta.max_limit
        elif self.relay:
            self.max_limit = kwargs.pop(
                "max_limit", graphene_settings.RELAY_CONNECTION_MAX_LIMIT
            )
        else:
            self.max_limit = None

        self.django_type = type
        kwargs.setdefault("offset", Int())

        if self.relay:
            super(DjangoConnectionField, self).__init__(type, *args, **kwargs)
        else:
            super(ConnectionField, self).__init__(type, *args, **kwargs)

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
            array_length=list_length,
            array_slice_length=list_slice_length,
            connection_type=partial(connection_adapter, connection),
            edge_type=connection.Edge,
            page_info_type=page_info_adapter,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection

    @classmethod
    def relay_connection_resolver(
        cls, resolver, connection, max_limit, enforce_first_or_last, root, info, **args
    ):

        # eventually leads to DjangoObjectType's get_queryset (accepts queryset)
        # or a resolve_foo (does not accept queryset)
        iterable = resolver(root, info, **args)
        on_resolve = partial(
            cls.resolve_connection, connection, args, max_limit=max_limit
        )

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)

        return on_resolve(iterable)

    @classmethod
    def connection_resolver(cls, resolver, connection, max_limit, root, info, **kwargs):
        start = kwargs.get("offset", 0)
        limit = kwargs.get("limit", max_limit)
        if limit is not None and max_limit is not None:
            if limit > max_limit:
                limit = max_limit
        if limit is not None:
            end = start + limit
        else:
            end = None
        iterable = resolver(root, info, **kwargs)
        connection = connection()
        connection.iterable = iterable
        connection.data = iterable[start:end]
        return connection

    def wrap_resolve(self, parent_resolver):

        resolver = partial(related_batchread, self.django_type, parent_resolver.args[0])

        if self.relay:
            return partial(
                self.relay_connection_resolver,
                resolver,
                self.connection_type,
                self.max_limit,
                self.enforce_first_or_last,
            )
        else:
            return partial(
                self.connection_resolver,
                resolver,
                self.connection_type,
                self.max_limit,
            )
