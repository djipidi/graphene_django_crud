# -*- coding: utf-8 -*-
import inspect
import re
from collections import OrderedDict

import six
from django import VERSION as DJANGO_VERSION
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRel
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db.models import (
    NOT_PROVIDED,
    QuerySet,
    Manager,
    Model,
    ManyToOneRel,
    ManyToManyRel,
    OneToOneRel,
    ForeignKey,
    ManyToManyField,
    OneToOneField
)
from django.db.models.base import ModelBase
from graphene.utils.str_converters import to_snake_case
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLList, GraphQLNonNull
from graphql.language.ast import FragmentSpread, InlineFragment

from django.conf import settings


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


def get_model_fields(model, only_fields="__all__", exclude_fields=(), to_dict=False):
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
                local_fields.append((field.name, field))
            elif isinstance(field, (ManyToManyRel, ManyToOneRel)):
                if field.related_name == None:
                    local_fields.append((field.name + '_set', field))
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
        is_include = False
        if str(name).endswith("+"):
            continue

        if only_fields == "__all__" and name not in exclude_fields:
            is_include = True
        elif name in only_fields:
            is_include = True

        if is_include:
            if to_dict:
                fields[name] = field
            else:
                fields.append((name, field))
    return fields

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


MANY_NESTED_FIELD = (ManyToManyField, ManyToOneRel)
ONE_NESTED_FIELD = (OneToOneRel, OneToOneField, ForeignKey)
def field_to_relation_type(model, field_name):
    field = get_model_fields(model, to_dict=True)[field_name]
    if isinstance(field, MANY_NESTED_FIELD):
        return "MANY"
    elif isinstance(field, ONE_NESTED_FIELD):
        return "ONE"
    else:
        return "ATTRIBUTE"