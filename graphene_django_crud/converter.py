# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
    GenericRel,
)
from django.db import models
from django.utils.encoding import force_text
import graphene
from graphene import (
    Field,
    ID,
    Boolean,
    Dynamic,
    Enum,
    Float,
    Int,
    List,
    NonNull,
    String,
    UUID,
    DateTime,
    Date,
    Time
)
from graphene.types.json import JSONString
from graphene.utils.str_converters import to_camel_case, to_const
from graphene_django.compat import ArrayField, HStoreField, RangeField, JSONField
from graphene_django.utils import import_single_dispatch

from .base_types import (
    GenericForeignKeyType,
    GenericForeignKeyInputType,
    Binary,
)
from .fields import DjangoListField
from .utils import is_required, get_model_fields, get_related_model

from .input_types import *

singledispatch = import_single_dispatch()


NAME_PATTERN = r"^[_a-zA-Z][_a-zA-Z0-9]*$"
COMPILED_NAME_PATTERN = re.compile(NAME_PATTERN)



def convert_model_to_input_type(model, input_flag="create", registry=None):


    input_type_name = '{}_{}_input'.format(model.__name__, input_flag.capitalize())
    input_type_name = to_camel_case(input_type_name)
    input_type = registry.get_type_for_input(input_type_name)
    if input_type:
        return input_type

    where_with_operator = False
    if input_flag == "where_with_operator":
        where_with_operator = True
        input_flag = "where"


    def embeded_list_fields():
        return graphene.List(convert_model_to_input_type(model, input_flag="where_with_operator", registry=registry))
    
    def embeded_field():
        return graphene.Field(convert_model_to_input_type(model, input_flag="where_with_operator", registry=registry))
    
    djangoType = registry.get_type_for_model(model)
    if "create" in input_flag or "update" in input_flag:
        model_fields = get_model_fields(
            model,
            only_fields = djangoType._meta.input_only_fields,
            exclude_fields = djangoType._meta.input_exclude_fields
        )
    else:
        model_fields = get_model_fields(
            model,
            only_fields = djangoType._meta.only_fields,
            exclude_fields = djangoType._meta.exclude_fields
        )


    items = OrderedDict()

    if input_flag == "create_nested_many":
        items["create"] = graphene.List(convert_model_to_input_type(model, input_flag="create", registry=registry))
        items["connect"] = graphene.List(convert_model_to_input_type(model, input_flag="where", registry=registry))
    
    elif input_flag == "update_nested_many":
        items["create"] = graphene.List(convert_model_to_input_type(model, input_flag="create", registry=registry))
        items["remove"] = graphene.List(convert_model_to_input_type(model, input_flag="where", registry=registry))
        items["connect"] = graphene.List(convert_model_to_input_type(model, input_flag="where", registry=registry))
        items["disconnect"] = graphene.List(convert_model_to_input_type(model, input_flag="where", registry=registry))

    elif input_flag == "create_nested":
        items["create"] = graphene.Field(convert_model_to_input_type(model, input_flag="create", registry=registry))
        items["connect"] = graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))

    elif input_flag == "update_nested":
        items["create"] = graphene.Field(convert_model_to_input_type(model, input_flag="create", registry=registry))
        # items["remove"] = graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
        items["connect"] = graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
        # items["disconnect"] = graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
 
    else:
        for name, field in model_fields:
            if name == "id" and ("create" in input_flag or "update" in input_flag):
                continue
            if input_flag == "where_unique":
                try :
                    if not field.unique:
                        continue
                except AttributeError:#for manytomany relation
                    continue

            converted = convert_django_field_with_choices(field, input_flag=input_flag, registry=registry)
            items[name] = converted
        if where_with_operator:
            items["OR"] = graphene.Dynamic(embeded_list_fields)
            items["AND"] = graphene.Dynamic(embeded_list_fields)
            items["NOT"] = graphene.Dynamic(embeded_field)

    ret_type = type(
        input_type_name,
        (graphene.InputObjectType,),
        items,
    )

    registry.register_input(input_type_name, ret_type)
    return ret_type


def assert_valid_name(name):
    """ Helper to assert that provided names are valid. """
    assert COMPILED_NAME_PATTERN.match(
        name
    ), 'Names must match /{}/ but "{}" does not.'.format(NAME_PATTERN, name)


def convert_choice_name(name):
    name = to_const(force_text(name))
    try:
        assert_valid_name(name)
    except AssertionError:
        name = "A_%s" % name
    return name


def get_choices(choices):
    converted_names = []
    for value, help_text in choices:
        if isinstance(help_text, (tuple, list)):
            for choice in get_choices(help_text):
                yield choice
        else:
            name = convert_choice_name(value)
            while name in converted_names:
                name += "_" + str(len(converted_names))
            converted_names.append(name)
            description = help_text
            yield name, value, description


def convert_django_field_with_choices(
    field, registry=None, input_flag=None
):
    choices = getattr(field, "choices", None)
    if choices:
        meta = field.model._meta

        name = "{}_{}_{}".format(meta.object_name, field.name, "Enum")
        # if input_flag:
        #     name = "{}_{}".format(name, input_flag)
        name = to_camel_case(name)

        enum = registry.get_type_for_enum(name)
        if not enum:
            choices = list(get_choices(choices))
            named_choices = [(c[0], c[1]) for c in choices]
            named_choices_descriptions = {c[0]: c[2] for c in choices}

            class EnumWithDescriptionsType(object):
                @property
                def description(self):
                    return named_choices_descriptions[self.name]

            enum = Enum(name, list(named_choices), type=EnumWithDescriptionsType)
            registry.register_enum(name, enum)

        if type(field).__name__ == "MultiSelectField":
            return DjangoListField(
                enum,
                description=field.help_text or field.verbose_name,
                required=is_required(field) and input_flag == "create",
            )
        return enum(
            description=field.help_text or field.verbose_name,
            required=is_required(field) and input_flag == "create",
        )
    return convert_django_field(field, registry, input_flag)


def construct_fields(
    model,
    registry,
    only_fields,
    exclude_fields,
):
    _model_fields = get_model_fields(model, only_fields=only_fields, exclude_fields=exclude_fields)

    if settings.DEBUG:
            _model_fields = sorted(_model_fields, key=lambda f: f[0])

    fields = OrderedDict()

    
    for name, field in _model_fields:

        converted = convert_django_field_with_choices(
            field, registry
        )
        fields[name] = converted
    return fields


@singledispatch
def convert_django_field(field, registry=None, input_flag=None):
    raise Exception(
        "Don't know how to convert the Django field {} ({})".format(
            field, field.__class__
        )
    )


@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.GenericIPAddressField)
@convert_django_field.register(models.FileField)
def convert_field_to_string(field, registry=None, input_flag=None):
    if input_flag == "where":
        return StringFilter()
    return String(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.AutoField)
def convert_field_to_id(field, registry=None, input_flag=None):

    if input_flag:
        if input_flag == "where":
            return IntFilter()
        return ID(
            description=field.help_text or "Django object unique identification field",
        )
    return ID(
        description=field.help_text or "Django object unique identification field",
        required=not field.null,
    )


@convert_django_field.register(models.UUIDField)
def convert_field_to_uuid(field, registry=None, input_flag=None):
    return UUID(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def convert_field_to_int(field, registry=None, input_flag=None):
    if input_flag == "where":
        return IntFilter()
    return Int(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(field, registry=None, input_flag=None):
    required = is_required(field) and input_flag == "create"
    if required:
        return NonNull(Boolean, description=field.help_text or field.verbose_name)
    return Boolean(description=field.help_text)


@convert_django_field.register(models.NullBooleanField)
def convert_field_to_nullboolean(
    field, registry=None, input_flag=None
):
    return Boolean(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.BinaryField)
def convert_binary_to_string(field, registry=None, input_flag=None):
    return Binary(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
@convert_django_field.register(models.DurationField)
def convert_field_to_float(field, registry=None, input_flag=None):
    if input_flag == "where":
        return FloatFilter()
    return Float(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DateField)
def convert_date_to_string(field, registry=None, input_flag=None):
    if input_flag == "where":
        return DateFilter()
    return Date(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DateTimeField)
def convert_datetime_to_string(
    field, registry=None, input_flag=None
):
    if input_flag == "where":
        return DateTimeFilter()
    return DateTime(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.TimeField)
def convert_time_to_string(field, registry=None, input_flag=None):
    if input_flag == "where":
        return TimeFilter()
    return Time(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.OneToOneRel)
def convert_onetoone_field_to_djangomodel(
    field, registry=None, input_flag=None
):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return


        if input_flag:
            if input_flag == "where":
                return graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
            elif input_flag == "create" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="create_nested", registry=registry))
            elif input_flag == "update" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="update_nested", registry=registry))

        return Field(_type, required=is_required(field) and input_flag == "create")

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
@convert_django_field.register(models.ManyToManyField)
def convert_many_rel_to_djangomodel(
    field, registry=None, input_flag=None
):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if input_flag:
            #return DjangoListField(ID)
            if input_flag == "where":
                return graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
            elif input_flag == "create" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="create_nested_many", registry=registry))
            elif input_flag == "update" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="update_nested_many", registry=registry))
        else:
            args = OrderedDict()
            args.update({
                "where": graphene.Argument(convert_model_to_input_type(model, input_flag="where", registry=registry)),
                "limit": graphene.Int(),
                "offset" : graphene.Int(),
                "orderBy" : graphene.List(graphene.String)
            }) 
            return DjangoListField(
                _type, required=is_required(field) and input_flag == "create", args=args
            )

    return Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(
    field, registry=None, input_flag=None
):
    model = get_related_model(field)

    def dynamic_type():

        _type = registry.get_type_for_model(model, for_input=input_flag)
        if not _type:
            return
        # Avoid create field for auto generate OneToOneField product of an inheritance
        if isinstance(field, models.OneToOneField) and issubclass(
            field.model, field.related_model
        ):
            return
        if input_flag:
            if input_flag == "where":
                return graphene.Field(convert_model_to_input_type(model, input_flag="where", registry=registry))
            elif input_flag == "where_unique":
                return graphene.Field(convert_model_to_input_type(model, input_flag="where_unique", registry=registry))
            elif input_flag == "create" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="create_nested", registry=registry))
            elif input_flag == "update" :
                return graphene.Field(convert_model_to_input_type(model, input_flag="update_nested", registry=registry))

        return Field(
            _type,
            description=field.help_text or field.verbose_name,
            required=is_required(field) and input_flag == "create",
        )

    return Dynamic(dynamic_type)


# @convert_django_field.register(GenericForeignKey)
# def convert_generic_foreign_key_to_object(
#     field, registry=None, input_flag=None
# ):
#     def dynamic_type():
#         key = "{}_{}".format(field.name, field.model.__name__.lower())
#         if input_flag is not None:
#             key = "{}_{}".format(key, input_flag)

#         key = to_camel_case(key)
#         model = field.model
#         ct_field = None
#         fk_field = None
#         required = False
#         for f in get_model_fields(model):
#             if f[0] == field.ct_field:
#                 ct_field = f[1]
#             elif f[0] == field.fk_field:
#                 fk_field = f[1]
#             if fk_field is not None and ct_field is not None:
#                 break

#         if ct_field is not None and fk_field is not None:
#             required = (is_required(ct_field) and is_required(fk_field)) or required

#         if input_flag:
#             return GenericForeignKeyInputType(
#                 description="Input Type for a GenericForeignKey field",
#                 required=required and input_flag == "create",
#             )

#         _type = registry.get_type_for_enum(key)
#         if not _type:
#             _type = GenericForeignKeyType

#         # return Field(_type, description=field.help_text or field.verbose_name, required=field.null)
#         return Field(
#             _type,
#             description="Type for a GenericForeignKey field",
#             required=required and input_flag == "create",
#         )

#     return Dynamic(dynamic_type)


# @convert_django_field.register(GenericRelation)
# def convert_generic_relation_to_object_list(
#     field, registry=None, input_flag=None
# ):
#     model = field.related_model

#     def dynamic_type():
#         if input_flag:
#             return

#         _type = registry.get_type_for_model(model)
#         if not _type:
#             return
#         return DjangoListField(_type)

#     return Dynamic(dynamic_type)


# @convert_django_field.register(ArrayField)
# def convert_postgres_array_to_list(
#     field, registry=None, input_flag=None
# ):
#     base_type = convert_django_field(field.base_field)
#     if not isinstance(base_type, (List, NonNull)):
#         base_type = type(base_type)
#     return List(
#         base_type,
#         description=field.help_text or field.verbose_name,
#         required=is_required(field) and input_flag == "create",
#     )


# @convert_django_field.register(HStoreField)
# @convert_django_field.register(JSONField)
# def convert_postgres_field_to_string(
#     field, registry=None, input_flag=None
# ):
#     return JSONString(
#         description=field.help_text or field.verbose_name,
#         required=is_required(field) and input_flag == "create",
#     )


# @convert_django_field.register(RangeField)
# def convert_postgres_range_to_string(
#     field, registry=None, input_flag=None
# ):
#     inner_type = convert_django_field(field.base_field)
#     if not isinstance(inner_type, (List, NonNull)):
#         inner_type = type(inner_type)
#     return List(
#         inner_type,
#         description=field.help_text or field.verbose_name,
#         required=is_required(field) and input_flag == "create",
#     )
