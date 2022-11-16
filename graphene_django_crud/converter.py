# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.utils.encoding import force_str as force_text
import graphene
from graphene import (
    Field,
    InputField,
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
    Time,
)

from graphene.utils.str_converters import to_camel_case
from functools import singledispatch

from .base_types import Binary, OrderEnum, OrderStringEnum, File
from .fields import DjangoListField, DjangoConnectionField
from .settings import gdc_settings
from .utils import is_required, get_model_fields, get_related_model, is_include

from .input_types import (
    BooleanFilter,
    FileInput,
    IDfilter,
    IntFilter,
    DecimalFilter,
    FloatFilter,
    StringFilter,
    DateTimeFilter,
    TimeFilter,
    DateFilter,
    UUIDFilter,
)


NAME_PATTERN = r"^[_a-zA-Z][_a-zA-Z0-9]*$"
COMPILED_NAME_PATTERN = re.compile(NAME_PATTERN)


def make_input_type(name, definition, registry=None):
    ret_type = type(
        name,
        (graphene.InputObjectType,),
        definition,
    )

    registry.register_input(name, ret_type)
    return ret_type


def get_input_type_name(model, input_flag, complement=None):
    if complement is None or complement == "":
        complement = ""
    else:
        complement += "_"
    return to_camel_case("{}_{}_{}input".format(model.__name__, input_flag, complement))


def convert_model_to_input_type(
    model, input_flag=None, registry=None, exclude=[], only="__all__"
):

    assert input_flag is not None

    django_type = registry.get_type_for_model(model)

    for_queryset = "order_by" in input_flag or "where" in input_flag

    model_fields = get_model_fields(django_type._meta.model, for_queryset=for_queryset)

    if "create" in input_flag or "update" in input_flag:
        model_fields = filter(
            lambda field: is_include(
                field[0],
                django_type._meta.input_only_fields,
                django_type._meta.input_exclude_fields,
            ),
            model_fields,
        )
        if "create" in input_flag:
            model_fields = filter(
                lambda field: is_include(
                    field[0],
                    django_type._meta.create_only_fields,
                    django_type._meta.create_exclude_fields,
                ),
                model_fields,
            )
        elif "update" in input_flag:
            model_fields = filter(
                lambda field: is_include(
                    field[0],
                    django_type._meta.update_only_fields,
                    django_type._meta.update_exclude_fields,
                ),
                model_fields,
            )
    else:
        model_fields = filter(
            lambda field: is_include(
                field[0],
                django_type._meta.only_fields,
                django_type._meta.exclude_fields,
            ),
            model_fields,
        )
        if "where" in input_flag:
            model_fields = filter(
                lambda field: is_include(
                    field[0],
                    django_type._meta.where_only_fields,
                    django_type._meta.where_exclude_fields,
                ),
                model_fields,
            )
        if "order_by" in input_flag:
            model_fields = filter(
                lambda field: is_include(
                    field[0],
                    django_type._meta.order_by_only_fields,
                    django_type._meta.order_by_exclude_fields,
                ),
                model_fields,
            )

    input_type_name_without_complement = ""
    if not (len(exclude) == 0 and only == "__all__"):
        it = model_fields
        model_fields = []
        exclude_fields = []
        for name, field in it:
            if not is_include(name, only, exclude):
                exclude_fields.append(name)
            else:
                model_fields.append((name, field))
        exclude_fields.sort()
        input_type_name_without_complement = "without_" + "_".join(exclude_fields)
    else:
        model_fields = list(model_fields)

    input_type_name = get_input_type_name(
        model, input_flag, complement=input_type_name_without_complement
    )

    input_type = registry.get_type_for_input(input_type_name)
    if input_type is not None:
        return input_type

    items = OrderedDict()

    if input_flag == "create_nested_many":
        if django_type._meta.create_mutation:
            items["create"] = graphene.List(
                convert_model_to_input_type(
                    model, input_flag="create", registry=registry
                )
            )
        items["connect"] = graphene.List(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )

    elif input_flag == "update_nested_many":
        if django_type._meta.create_mutation:
            items["create"] = graphene.List(
                convert_model_to_input_type(
                    model, input_flag="create", registry=registry
                )
            )
        if django_type._meta.update_mutation:
            items["update"] = graphene.List(
                convert_model_to_input_type(
                    model, input_flag="update_with_where", registry=registry
                )
            )
        if django_type._meta.delete_mutation:
            items["delete"] = graphene.List(
                convert_model_to_input_type(
                    model, input_flag="where", registry=registry
                )
            )
        items["connect"] = graphene.List(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )
        items["disconnect"] = graphene.List(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )

    elif input_flag == "create_nested":
        if django_type._meta.create_mutation:
            items["create"] = graphene.InputField(
                convert_model_to_input_type(
                    model, input_flag="create", exclude=exclude, registry=registry
                )
            )
        items["connect"] = graphene.InputField(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )

    elif input_flag == "update_nested":
        if django_type._meta.create_mutation:
            items["create"] = graphene.InputField(
                convert_model_to_input_type(
                    model, input_flag="create", exclude=exclude, registry=registry
                )
            )
        if django_type._meta.update_mutation:
            items["update"] = graphene.InputField(
                convert_model_to_input_type(
                    model, input_flag="update", registry=registry
                )
            )
        if django_type._meta.delete_mutation:
            items["delete"] = Boolean()
        items["connect"] = graphene.InputField(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )
        items["disconnect"] = Boolean()

    elif input_flag == "update_with_where":
        items["where"] = graphene.InputField(
            convert_model_to_input_type(model, input_flag="where", registry=registry)
        )
        items["input"] = graphene.InputField(
            convert_model_to_input_type(model, input_flag="update", registry=registry)
        )

    else:
        if input_flag == "where":

            def embeded_list_fields():
                return InputField(
                    graphene.List(
                        convert_model_to_input_type(
                            model, input_flag="where", registry=registry
                        )
                    )
                )

            def embeded_field():
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="where", registry=registry
                    )
                )

            items["id"] = IDfilter()
            items["OR"] = graphene.Dynamic(embeded_list_fields)
            items["AND"] = graphene.Dynamic(embeded_list_fields)
            items["NOT"] = graphene.Dynamic(embeded_field)

        for name, field in model_fields:
            if name == "id" and input_flag in ["create", "update", "where"]:
                continue

            converted = convert_django_field_with_choices(
                field, input_flag=input_flag, registry=registry
            )
            items[name] = converted

        if "create" in input_flag or "update" in input_flag:
            for name, field in django_type._meta.input_extend_fields:
                items[name] = field
            if "create" in input_flag:
                for name, field in django_type._meta.create_extend_fields:
                    items[name] = field
            elif "update" in input_flag:
                for name, field in django_type._meta.update_extend_fields:
                    items[name] = field

    return make_input_type(input_type_name, items, registry=registry)


def assert_valid_name(name):
    """Helper to assert that provided names are valid."""
    assert COMPILED_NAME_PATTERN.match(
        name
    ), 'Names must match /{}/ but "{}" does not.'.format(NAME_PATTERN, name)


def convert_choice_name(name):
    name = force_text(name)
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


def convert_django_field_with_choices(field, registry=None, input_flag=None):
    choices = getattr(field, "choices", None)
    if choices and not input_flag == "order_by" and gdc_settings.CONVERT_ENUM_FIELDS:
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
    _model_fields = get_model_fields(
        model, only_fields=only_fields, exclude_fields=exclude_fields
    )

    if settings.DEBUG:
        _model_fields = sorted(_model_fields, key=lambda f: f[0])

    fields = OrderedDict()
    fields["id"] = ID(description="unique identification field")
    for name, field in _model_fields:
        if name == "id":
            continue
        converted = convert_django_field_with_choices(field, registry)
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
def convert_field_to_string(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderStringEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return StringFilter(
            description=field.help_text or field.verbose_name,
        )
    return String(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.AutoField)
@convert_django_field.register(models.BigAutoField)
def convert_field_to_id(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag:
        if input_flag == "where":
            return IDfilter(
                description=field.help_text or field.verbose_name,
            )
        return ID(
            description=field.help_text or "Django object unique identification field",
        )
    return ID(
        description=field.help_text or "Django object unique identification field",
        required=not field.null,
    )


@convert_django_field.register(models.UUIDField)
def convert_field_to_uuid(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return UUIDFilter(
            description=field.help_text or field.verbose_name,
        )
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
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return IntFilter(
            description=field.help_text or field.verbose_name,
        )
    return Int(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return BooleanFilter(
            description=field.help_text or field.verbose_name,
        )
    required = is_required(field) and input_flag == "create"
    if required:
        return NonNull(Boolean, description=field.help_text or field.verbose_name)
    return Boolean(description=field.help_text)


@convert_django_field.register(models.NullBooleanField)
def convert_field_to_nullboolean(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return BooleanFilter(
            description=field.help_text or field.verbose_name,
        )
    return Boolean(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.BinaryField)
def convert_binary_to_string(field, registry=None, input_flag=None):
    if input_flag == "order_by" or input_flag == "where":
        return None
    return Binary(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
@convert_django_field.register(models.DurationField)
def convert_field_to_float(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return FloatFilter(
            description=field.help_text or field.verbose_name,
        )
    return Float(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DateField)
def convert_date_to_string(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return DateFilter(
            description=field.help_text or field.verbose_name,
        )
    return Date(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.DateTimeField)
def convert_datetime_to_string(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return DateTimeFilter(
            description=field.help_text or field.verbose_name,
        )
    return DateTime(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.TimeField)
def convert_time_to_string(field, registry=None, input_flag=None):
    if input_flag == "order_by":
        return OrderEnum(
            description=field.help_text or field.verbose_name,
        )
    if input_flag == "where":
        return TimeFilter(
            description=field.help_text or field.verbose_name,
        )
    return Time(
        description=field.help_text or field.verbose_name,
        required=is_required(field) and input_flag == "create",
    )


@convert_django_field.register(models.FileField)
@convert_django_field.register(models.ImageField)
def convert_field_to_file(field, registry=None, input_flag=None):
    if input_flag:
        if input_flag == "order_by":
            return OrderEnum(
                description=field.help_text or field.verbose_name,
            )
        elif input_flag == "where":
            return StringFilter(
                description=field.help_text or field.verbose_name,
            )
        else:
            return FileInput(
                description=field.help_text or field.verbose_name,
                required=is_required(field) and input_flag == "create",
            )
    return Field(
        File,
        description=field.help_text or field.verbose_name,
    )


@convert_django_field.register(models.OneToOneRel)
def convert_onetoone_field_to_djangomodel(field, registry=None, input_flag=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if input_flag:
            if input_flag == "order_by":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="order_by", registry=registry
                    ),
                )
            elif input_flag == "where":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="where", registry=registry
                    ),
                )
            elif input_flag == "create":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model,
                        input_flag="create_nested",
                        registry=registry,
                    ),
                )
            elif input_flag == "update":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model,
                        input_flag="update_nested",
                        registry=registry,
                    ),
                )

        return Field(
            _type,
        )

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ManyToOneRel)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToManyField)
def convert_many_rel_djangomodel(field, registry=None, input_flag=None):
    model = field.related_model
    if input_flag == "order_by":
        return

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if input_flag:
            if input_flag == "where":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="where", registry=registry
                    ),
                )
            elif input_flag == "create":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="create_nested_many", registry=registry
                    ),
                )
            elif input_flag == "update":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="update_nested_many", registry=registry
                    ),
                )
        else:
            args = dict()
            args.update(
                {
                    "where": graphene.Argument(
                        convert_model_to_input_type(
                            model, input_flag="where", registry=registry
                        )
                    ),
                    "order_by": graphene.List(
                        convert_model_to_input_type(
                            model, input_flag="order_by", registry=registry
                        )
                    ),
                }
            )

            if _type._meta.connection:
                return DjangoConnectionField(
                    _type,
                    **args,
                )

            return DjangoListField(
                _type,
                **args,
            )

    return Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneField)
def convert_ForeignKey_field_to_djangomodel(field, registry=None, input_flag=None):
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
            if input_flag == "order_by":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="order_by", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )

            elif input_flag == "where":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="where", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )
            elif input_flag == "create":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model,
                        input_flag="create_nested",
                        registry=registry,
                    ),
                    description=field.help_text or field.verbose_name,
                )
            elif input_flag == "update":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model,
                        input_flag="update_nested",
                        registry=registry,
                    ),
                    description=field.help_text or field.verbose_name,
                )

        return Field(
            _type,
            description=field.help_text or field.verbose_name,
        )

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ForeignKey)
def convert_ForeignKey_field_to_djangomodel(field, registry=None, input_flag=None):
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
            if input_flag == "order_by":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="order_by", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )
            elif input_flag == "where":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="where", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )
            elif input_flag == "create":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="create_nested", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )
            elif input_flag == "update":
                return graphene.InputField(
                    convert_model_to_input_type(
                        model, input_flag="update_nested", registry=registry
                    ),
                    description=field.help_text or field.verbose_name,
                )

        return Field(
            _type,
            description=field.help_text or field.verbose_name,
        )

    return Dynamic(dynamic_type)
