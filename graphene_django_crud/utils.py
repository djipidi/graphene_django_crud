# -*- coding: utf-8 -*-
import inspect
import re
from collections import OrderedDict

import six
from django import VERSION as DJANGO_VERSION
from django.apps import apps, registry
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db.models import (
    NOT_PROVIDED,
    Q,
    Model,
    ManyToOneRel,
    ManyToManyRel,
    OneToOneRel,
)
from graphql_relay import from_global_id
from graphene.utils.str_converters import to_camel_case
from graphene.types.scalars import MAX_INT, MIN_INT
from graphene import Dynamic, List
from graphql.language.ast import (
    FragmentSpreadNode,
    InlineFragmentNode,
    VariableNode,
    BooleanValueNode,
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    ObjectValueNode,
    StringValueNode,
    EnumValueNode,
)
from django.conf import settings
from django.db.models.functions import Lower
from .registry import get_global_registry

registry = get_global_registry()


def get_reverse_fields(model):
    reverse_fields = {
        f.name: f for f in model._meta.get_fields() if f.auto_created and not f.concrete
    }

    for name, field in reverse_fields.items():
        # Django =>1.9 uses 'rel', django <1.9 uses 'related'
        related = getattr(field, "rel", None) or getattr(field, "related", None)
        if isinstance(related, ManyToOneRel):
            yield (name, related)
        elif isinstance(related, ManyToManyRel) and not related.symmetrical:
            yield (name, related)


def _resolve_model(obj):
    """
    Resolve supplied `obj` to a Django model class.
    `obj` must be a Django model class itself, or a string
    representation of one.  Useful in situations like GH #1225 where
    Django may not have resolved a string-based reference to a model in
    another model's foreign key definition.
    String representations should have the format:
        'appname.ModelName'
    """
    if isinstance(obj, six.string_types) and len(obj.split(".")) == 2:
        app_name, model_name = obj.split(".")
        resolved_model = apps.get_model(app_name, model_name)
        if resolved_model is None:
            msg = "Django did not return a model for {0}.{1}"
            raise ImproperlyConfigured(msg.format(app_name, model_name))
        return resolved_model
    elif inspect.isclass(obj) and issubclass(obj, Model):
        return obj
    raise ValueError("{0} is not a Django model".format(obj))


def get_related_model(field):
    # Backward compatibility patch for Django versions lower than 1.9.x
    if DJANGO_VERSION < (1, 9):
        return _resolve_model(field.rel.to)
    return field.remote_field.model


def get_model_fields(
    model, only_fields="__all__", exclude_fields=(), to_dict=False, for_queryset=False
):
    # Backward compatibility patch for Django versions lower than 1.11.x
    if DJANGO_VERSION >= (1, 11):
        private_fields = model._meta.private_fields
    else:
        private_fields = model._meta.virtual_fields

    all_fields_list = (
        list(model._meta.fields)
        + list(model._meta.local_many_to_many)
        + list(private_fields)
        + list(model._meta.fields_map.values())
    )

    # Make sure we don't duplicate local fields with "reverse" version
    # and get the real reverse django related_name
    reverse_fields = list(get_reverse_fields(model))
    invalid_fields = [field[1] for field in reverse_fields]

    local_fields = []
    for field in all_fields_list:
        if field not in invalid_fields:
            if isinstance(field, OneToOneRel):
                if for_queryset:
                    if field.related_query_name is None:
                        local_fields.append((field.name, field))
                    else:
                        local_fields.append((field.related_query_name, field))
                else:
                    local_fields.append((field.name, field))
            elif isinstance(field, (ManyToManyRel, ManyToOneRel)):
                if for_queryset:
                    if field.related_query_name == None:
                        local_fields.append((field.name, field))
                    else:
                        local_fields.append((field.related_query_name, field))
                else:
                    if field.related_name == None:
                        local_fields.append((field.get_accessor_name(), field))
                    else:
                        local_fields.append((field.related_name, field))

            else:
                local_fields.append((field.name, field))

    all_fields = local_fields + reverse_fields

    if settings.DEBUG:
        all_fields = sorted(all_fields, key=lambda f: f[0])
    if to_dict:
        fields = {}
    else:
        fields = []

    for name, field in all_fields:
        if str(name).endswith("+"):
            continue
        if not is_include(name, only_fields, exclude_fields):
            continue

        if to_dict:
            fields[name] = field
        else:
            fields.append((name, field))

    return fields


def is_include(name, only_fields, exclude_fields):
    if only_fields == "__all__" and name not in exclude_fields:
        return True
    elif name in only_fields:
        return True
    return False


def is_required(field):
    try:
        blank = getattr(field, "blank", getattr(field, "field", None))
        default = getattr(field, "default", getattr(field, "field", None))
        #  null = getattr(field, "null", getattr(field, "field", None))

        if blank is None:
            blank = True
        elif not isinstance(blank, bool):
            blank = getattr(blank, "blank", True)

        if default is None:
            default = NOT_PROVIDED
        elif default != NOT_PROVIDED:
            default = getattr(default, "default", default)

    except AttributeError:
        return False

    return not blank and default == NOT_PROVIDED


def get_type_field(gql_type, gql_name):
    fields = gql_type._meta.fields
    for name, field in fields.items():
        if to_camel_case(gql_name) == to_camel_case(name):
            if isinstance(field, Dynamic):
                field = field.get_type()
            else:
                field = field
            if isinstance(field, List):
                field_type = field.of_type
            else:
                field_type = field.type
            if isinstance(field_type, List):
                field_type = field_type.of_type
            return name, field_type


def resolve_argument(input_type, argument):
    if isinstance(argument, list):
        ret = []
        for arg in argument:
            ret.append(resolve_argument(input_type, arg))
    elif isinstance(argument, dict):
        ret = {}
        for gql_name, value in argument.items():
            name, field_type = get_type_field(input_type, gql_name)
            if isinstance(value, (dict, list)):
                ret[name] = resolve_argument(field_type, value)
            else:
                ret[name] = value
    else:
        return argument
    return ret


def get_field_ast_by_path(info, path):
    path = path.copy()
    field_ast = info.field_nodes[0]
    while len(path) != 0:
        found = False
        iterator = [f for f in field_ast.selection_set.selections]
        for field in iterator:
            if isinstance(field, FragmentSpreadNode):
                iterator.extend(
                    [
                        f
                        for f in info.fragments[
                            field.name.value
                        ].selection_set.selections
                    ]
                )
            if isinstance(field, InlineFragmentNode):
                iterator.extend([f for f in field.selection_set.selections])
            if field.name.value == path[0]:
                field_ast = field
                del path[0]
                found = True
                break
        if not found:
            return None
    return field_ast


def parse_ast(ast, variable_values={}):
    if isinstance(ast, VariableNode):
        var_name = ast.name.value
        value = variable_values.get(var_name)
        return value
    elif isinstance(ast, (StringValueNode, BooleanValueNode)):
        return ast.value
    elif isinstance(ast, IntValueNode):
        num = int(ast.value)
        if MIN_INT <= num <= MAX_INT:
            return num
    elif isinstance(ast, FloatValueNode):
        return float(ast.value)
    elif isinstance(ast, EnumValueNode):
        return ast.value
    elif isinstance(ast, ListValueNode):
        ret = []
        for ast_value in ast.values:
            value = parse_ast(ast_value, variable_values=variable_values)
            if value is not None:
                ret.append(value)
        return ret
    elif isinstance(ast, ObjectValueNode):
        ret = {}
        for field in ast.fields:
            value = parse_ast(field.value, variable_values=variable_values)
            if value is not None:
                ret[field.name.value] = value
        return ret
    else:
        return None


def parse_arguments_ast(arguments, variable_values={}):
    ret = {}
    for argument in arguments:
        value = parse_ast(argument.value, variable_values=variable_values)
        if value is not None:
            ret[argument.name.value] = value
    return ret


def get_paths(d):
    q = [(d, [])]
    while q:
        n, p = q.pop(0)
        yield p
        if isinstance(n, dict):
            for k, v in n.items():
                q.append((v, p + [k]))


def nested_get(input_dict, nested_key):
    internal_dict_value = input_dict
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def get_args(where):
    args = {}
    for path in get_paths(where):
        arg_value = nested_get(where, path)
        if not isinstance(arg_value, dict):
            arg_key = "__".join(path)
            if arg_key.endswith("__equals"):
                arg_key = arg_key[0:-8] + "__exact"
            if (
                arg_key == "id__exact"
                or arg_key.endswith("__id__exact")
                or arg_key == "id__in"
                or arg_key.endswith("__id__in")
            ):
                if isinstance(arg_value, list):
                    try:
                        arg_value = [get_real_id(value) for value in arg_value]
                    except:
                        pass
                else:
                    try:
                        arg_value = get_real_id(arg_value)
                    except:
                        pass

            args[arg_key] = arg_value
    return args


def get_real_id(value):
    try:
        gql_type, relay_id = from_global_id(value)
        if registry.get_django_type(gql_type) is not None:
            return relay_id
        else:
            return value
    except:
        return value


def where_input_to_Q(where):

    AND = Q()
    OR = Q()
    NOT = Q()
    if "OR" in where.keys():
        for w in where.pop("OR"):
            OR = OR | Q(where_input_to_Q(w))

    if "AND" in where.keys():
        for w in where.pop("AND"):
            AND = AND & Q(where_input_to_Q(w))

    if "NOT" in where.keys():
        NOT = NOT & ~Q(where_input_to_Q(where.pop("NOT")))

    return Q(**get_args(where)) & OR & AND & NOT


def order_by_input_to_args(order_by):
    args = []
    for rule in order_by:
        for path in get_paths(rule):
            v = nested_get(rule, path)
            if not isinstance(v, dict):
                if v == "ASC":
                    args.append("__".join(path))
                elif v == "DESC":
                    args.append("-" + "__".join(path))
                elif v == "IASC":
                    args.append(Lower("__".join(path)).asc())
                elif v == "IDESC":
                    args.append(Lower("__".join(path)).desc())
    return args


def error_data_from_validation_error(validation_error):
    ret = []
    for field, error_list in validation_error.error_dict.items():
        messages = []
        for error in error_list:
            messages.extend(error.messages)
        ret.append({"field": field, "messages": messages})
    return ret


def validation_error_with_suffix(validation_error, suffix):
    error_dict = {}
    for field, error_list in validation_error.error_dict.items():
        error_dict[suffix + "." + field] = error_list
    return ValidationError(error_dict)
