# -*- coding: utf-8 -*-

import binascii

import graphene
from graphql.language import ast
from graphene_django.types import ErrorType

from .registry import get_global_registry


def mutation_factory_type(_type, registry=None, *args, **kwargs):
    if not registry:
        registry = get_global_registry()
    mutationTypeName = _type._meta.name.replace("Type", "") + "MutationType"
    mutationType = registry.get_type_for_mutation_type(mutationTypeName)
    if mutationType:
        return mutationType

    class MutationGenericType(graphene.ObjectType):
        class Meta:
            name = mutationTypeName

        ok = graphene.Boolean(
            description="Boolean field that return mutation result request."
        )
        errors = graphene.List(ErrorType, description="Errors list for the field")
        result = graphene.Field(_type)

    registry.register_mutation_type(mutationTypeName, MutationGenericType)

    return MutationGenericType


def node_factory_type(_type, registry=None, *args, **kwargs):
    if not registry:
        registry = get_global_registry()
    nodeTypeName = _type._meta.name.replace("Type", "") + "NodeType"
    nodeType = registry.get_type_for_node_type(nodeTypeName)
    if nodeType:
        return nodeType

    class NodeGenericType(graphene.ObjectType):
        class Meta:
            name = nodeTypeName

        count = graphene.Int()
        data = graphene.List(_type)

    registry.register_node_type(nodeTypeName, NodeGenericType)
    return NodeGenericType


class OrderEnum(graphene.Enum):
    ASC = "ASC"
    DESC = "DESC"


class Binary(graphene.Scalar):
    """
    BinaryArray is used to convert a Django BinaryField to the string form
    """

    @staticmethod
    def binary_to_string(value):
        return binascii.hexlify(value).decode("utf-8")

    serialize = binary_to_string
    parse_value = binary_to_string

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.binary_to_string(node.value)
