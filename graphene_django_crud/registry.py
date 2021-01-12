# -*- coding: utf-8 -*-
from graphene.utils.str_converters import to_camel_case


class Registry(object):

    def __init__(self):
        self._registry = {}
        self._registry_mutation_type = {}
        self._registry_node_type = {}
        self._registry_models = {}
        self._register_input = {}
        self._registry_directives = {}

        self.model_to_type_index = {}

    def register_enum(self, key, enum):
        self._registry[key] = enum

    def get_type_for_enum(self, key):
        return self._registry.get(key)

    def register_input(self, name, inputType):
        self._register_input[name] = inputType

    def get_type_for_input(self, name):
        return self._register_input.get(name)

    def register_mutation_type(self, name, mutationType):
        self._registry_mutation_type[name] = mutationType

    def get_type_for_mutation_type(self, name):
        return self._registry_mutation_type.get(name)

    def register_node_type(self, name, mutationType):
        self._registry_node_type[name] = mutationType

    def get_type_for_node_type(self, name):
        return self._registry_node_type.get(name)

    def register_directive(self, name, directive):
        self._registry_directives[name] = directive

    def get_directive(self, name):
        return self._registry_directives.get(name)

    def register_django_type(self, cls):
        if not getattr(cls._meta, "skip_registry", False):
            self._registry[cls.__name__] = cls
            self.model_to_type_index[cls._meta.model] = cls


    def get_type_for_model(self, model, for_input=None):
        return self.model_to_type_index.get(model, None)


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None
