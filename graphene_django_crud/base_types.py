# -*- coding: utf-8 -*-

import binascii
from collections import OrderedDict

import graphene
from graphene.types.field import Field
from graphene.types.structures import List, NonNull
from graphql.language import ast
from graphene_django.types import ErrorType
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
import re
from .registry import get_global_registry
import base64
from .settings import gdc_settings
from graphene.utils.str_converters import to_camel_case


def get_mutation_payload_type(_type, mutation_flag, registry=None, *args, **kwargs):
    if not registry:
        registry = get_global_registry()
    mutation_payload_type_name = to_camel_case(
        f"{_type._meta.model.__name__}_{mutation_flag}_payload"
    )
    mutationType = registry.get_type_for_mutation_type(mutation_payload_type_name)
    if mutationType:
        return mutationType

    class MutationPayloadGenericType(graphene.ObjectType):
        class Meta:
            name = mutation_payload_type_name

        ok = graphene.Boolean(
            description="Boolean field that return the success state of request."
        )
        errors = graphene.List(ErrorType, description="Errors list for the field")
        if not mutation_flag == "delete":
            result = graphene.Field(_type)

    MutationPayloadGenericType.__name__ = mutation_payload_type_name

    registry.register_mutation_type(mutation_payload_type_name, MutationPayloadGenericType)

    return MutationPayloadGenericType


class ConnectionOptions(ObjectTypeOptions):
    node = None


class EmptyDefaultConnection(ObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        _meta = ConnectionOptions(cls)

        base_name = re.sub("Connection$", "", name or cls.__name__) or node._meta.name
        if not name:
            name = "{}Connection".format(base_name)

        _node = node

        options["name"] = name
        _meta.node = node
        _meta.fields = OrderedDict(
            [
                (
                    gdc_settings.DEFAULT_CONNECTION_NODES_FIELD_NAME,
                    Field(
                        NonNull(List(_node)),
                        description="Contains the nodes in this connection.",
                        resolver=cls.resolve_data,
                    ),
                ),
            ]
        )
        return super(EmptyDefaultConnection, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )

    def resolve_data(self, info, *args, **kwargs):
        return self.data


class DefaultConnection(EmptyDefaultConnection):
    count = graphene.Int()

    def resolve_count(self, info, *args, **kwargs):
        return self.iterable.count()


class OrderEnum(graphene.Enum):
    ASC = "ASC"
    DESC = "DESC"


class OrderStringEnum(graphene.Enum):
    ASC = "ASC"
    DESC = "DESC"
    IASC = "IASC"
    IDESC = "IDESC"


class Binary(graphene.Scalar):
    """
    BinaryArray is used to convert a Django BinaryField to the string form
    """

    @staticmethod
    def binary_to_string(value):
        return base64.b64encode(value).decode("utf-8")

    @staticmethod
    def string_to_binary(value):
        return base64.b64decode(value)

    serialize = binary_to_string
    parse_value = string_to_binary

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.string_to_binary(node.value)


class File(graphene.ObjectType):
    url = graphene.String()
    size = graphene.Int()
    filename = graphene.String()
    if gdc_settings.FILE_TYPE_CONTENT_FIELD_ACTIVE:
        content = Binary()

    @staticmethod
    def resolve_url(parent, info, **kwargs):
        try:
            return parent.url
        except ValueError:
            return None

    @staticmethod
    def resolve_size(parent, info, **kwargs):
        try:
            return parent.size
        except ValueError:
            return None

    @staticmethod
    def resolve_filename(parent, info, **kwargs):
        try:
            return parent.name
        except ValueError:
            return None

    @staticmethod
    def resolve_content(parent, info, **kwargs):
        try:
            return parent.read()
        except ValueError:
            return None
