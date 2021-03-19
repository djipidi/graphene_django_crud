# -*- coding: utf-8 -*-

from collections import OrderedDict
import graphene
from graphene.types.base import BaseOptions
from graphene_django.types import ErrorType
from graphql.language.ast import FragmentSpread, InlineFragment, Variable
from graphene.utils.str_converters import to_camel_case

from .utils import (
    get_related_model,
    get_model_fields,
    parse_arguments_ast,
    get_field_ast_by_path,
)
from .base_types import mutation_factory_type, node_factory_type

from django.db import models, transaction
from django.db.models import Q, Prefetch
from django.core.exceptions import ValidationError

from .converter import convert_model_to_input_type, construct_fields
from .registry import get_global_registry, Registry

from graphene_subscriptions.events import CREATED, UPDATED, DELETED

from graphene.types.utils import yank_fields_from_attrs

from django.db.models.signals import post_save, post_delete, pre_delete
from graphene_subscriptions.signals import (
    post_save_subscription,
    post_delete_subscription,
)

from django.db.models import (
    ManyToOneRel,
    ManyToManyRel,
    OneToOneRel,
    ForeignKey,
    ManyToManyField,
    OneToOneField,
)


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
        v = nested_get(where, path)
        if not isinstance(v, dict):
            args["__".join(path).replace("__equals", "")] = v
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


def apply_where(where):

    AND = Q()
    OR = Q()
    NOT = Q()
    if "OR" in where.keys():
        for w in where.pop("OR"):
            OR = OR | Q(apply_where(w))

    if "AND" in where.keys():
        for w in where.pop("AND"):
            AND = AND & Q(apply_where(w))

    if "NOT" in where.keys():
        NOT = NOT & ~Q(apply_where(where.pop("NOT")))

    return Q(**get_args(where)) & OR & AND & NOT


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def resolver_hints(select_related=[], only=[], **kwargs):
    def wrapper(f):
        f.select_related = select_related
        f.only = only
        f.have_resolver_hints = True
        return f

    return wrapper


class DjangoGrapheneCRUDOptions(BaseOptions):
    model = None

    max_limit = None

    only_fields = "__all__"
    exclude_fields = ()

    input_only_fields = "__all__"
    input_exclude_fields = ()
    input_extend_fields = ()

    interfaces = ()

    registry = (None,)


class DjangoGrapheneCRUD(graphene.ObjectType):
    """
    Mutation, query Type Definition
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        max_limit=None,
        only_fields="__all__",
        exclude_fields=(),
        input_only_fields="__all__",
        input_exclude_fields=(),
        input_extend_fields=(),
        description="",
        registry=None,
        skip_registry=False,
        **options,
    ):

        if not model:
            raise Exception("model is required on all DjangoGrapheneCRUD")

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            "The attribute registry in {} needs to be an instance of "
            'Registry, received "{}".'
        ).format(cls.__name__, registry)

        description = description or "type for {} model".format(model.__name__)

        fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields),
            _as=graphene.Field,
        )

        _meta = DjangoGrapheneCRUDOptions(cls)
        _meta.model = model
        _meta.max_limit = max_limit
        _meta.fields = fields
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields

        _meta.input_only_fields = input_only_fields
        _meta.input_exclude_fields = input_exclude_fields

        _meta.input_extend_fields = input_extend_fields

        _meta.registry = registry

        super(DjangoGrapheneCRUD, cls).__init_subclass_with_meta__(
            _meta=_meta, description=description, **options
        )

        if not skip_registry:
            registry.register_django_type(cls)

    @classmethod
    def _queryset_factory(cls, info, field_ast=None, node=True, **kwargs):

        queryset = cls.get_queryset(None, info)
        arguments = parse_arguments_ast(
            field_ast.arguments, variable_values=info.variable_values
        )

        queryset_factory = cls._queryset_factory_analyze(
            info, field_ast.selection_set, node=node
        )

        queryset = queryset.select_related(*queryset_factory["select_related"])
        queryset = queryset.only(*queryset_factory["only"])
        queryset = queryset.prefetch_related(*queryset_factory["prefetch_related"])
        queryset = queryset.filter(apply_where(arguments.get("where", {})))
        if "orderBy" in arguments.keys():
            queryset = queryset.order_by(*arguments.get("orderBy", []))
        queryset = queryset.distinct()
        return queryset

    @classmethod
    def _queryset_factory_analyze(cls, info, selection_set, node=True, suffix=""):
        def fusion_ret(a, b):

            [
                a["select_related"].append(x)
                for x in b["select_related"]
                if x not in a["select_related"]
            ]
            [a["prefetch_related"].append(x) for x in b["prefetch_related"]]
            [a["only"].append(x) for x in b["only"] if x not in a["only"]]
            return a

        ret = {"select_related": [], "only": ["pk"], "prefetch_related": []}

        if suffix == "":
            new_suffix = ""
        else:
            new_suffix = suffix + "__"

        model_fields = get_model_fields(cls._meta.model, to_dict=True)
        fields_name_mapper = {}
        computed_field_hints = {}
        for field_name, field in cls._meta.fields.items():
            if field_name in model_fields.keys():
                continue
            if field.resolver is None:
                resolver = cls.__dict__.get("resolve_" + field_name, None)
            else:
                resolver = field.resolver
            if resolver is not None and hasattr(resolver, "have_resolver_hints"):
                fields_name_mapper[to_camel_case(field_name)] = field_name
                computed_field_hints[field_name] = {
                    "only": resolver.only,
                    "select_related": resolver.select_related,
                    "prefetch_related": [],
                }

        for k in model_fields.keys():
            fields_name_mapper[to_camel_case(k)] = k

        for field in selection_set.selections:
            if isinstance(field, FragmentSpread):
                new_ret = cls._queryset_factory_analyze(
                    info,
                    info.fragments[field.name.value].selection_set,
                    suffix=suffix,
                    node=node,
                )
                ret = fusion_ret(ret, new_ret)
                continue

            if isinstance(field, InlineFragment):
                new_ret = cls._queryset_factory_analyze(
                    info,
                    field.selection_set,
                    suffix=suffix,
                    node=node,
                )
                ret = fusion_ret(ret, new_ret)
                continue

            if node:
                if field.name.value == "data":
                    new_ret = cls._queryset_factory_analyze(
                        info,
                        field.selection_set,
                        suffix=new_suffix,
                        node=False,
                    )
                    ret = fusion_ret(ret, new_ret)
            else:
                try:
                    model_field = model_fields[fields_name_mapper[field.name.value]]
                except KeyError:
                    try:
                        computed_field = computed_field_hints[
                            fields_name_mapper[field.name.value]
                        ]
                    except KeyError:
                        continue
                    ret = fusion_ret(ret, computed_field)
                    continue

                if getattr(field, "selection_set", None):
                    related_type = get_global_registry().get_type_for_model(
                        model_field.remote_field.model
                    )
                    if isinstance(
                        model_field, (OneToOneField, OneToOneRel, ForeignKey)
                    ):
                        ret["select_related"].append(
                            new_suffix + fields_name_mapper[field.name.value]
                        )
                        new_ret = related_type._queryset_factory_analyze(
                            info,
                            field.selection_set,
                            node=False,
                            suffix=new_suffix + fields_name_mapper[field.name.value],
                        )
                        ret = fusion_ret(ret, new_ret)
                    elif isinstance(
                        model_field, (ManyToManyField, ManyToManyRel, ManyToOneRel)
                    ):
                        ret["prefetch_related"].append(
                            Prefetch(
                                new_suffix + fields_name_mapper[field.name.value],
                                queryset=related_type._queryset_factory(
                                    info, field_ast=field, node=True
                                ),
                            )
                        )

                else:
                    ret["only"].append(
                        new_suffix + fields_name_mapper[field.name.value]
                    )
        return ret

    @classmethod
    def _instance_to_queryset(cls, info, instance, field_ast):
        queryset = cls._queryset_factory(info, field_ast=field_ast, node=False)
        queryset = queryset.filter(pk=instance.pk)
        return queryset

    @classmethod
    def generate_signals(cls):
        post_save.connect(post_save_subscription, sender=cls._meta.model)
        post_delete.connect(post_delete_subscription, sender=cls._meta.model)

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        return cls._meta.model.objects.all()

    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        pass

    @classmethod
    def before_create(cls, parent, info, instance, data):
        pass

    @classmethod
    def before_update(cls, parent, info, instance, data):
        pass

    @classmethod
    def before_delete(cls, parent, info, instance, data):
        pass

    @classmethod
    def after_mutate(cls, parent, info, instance, data):
        pass

    @classmethod
    def after_create(cls, parent, info, instance, data):
        pass

    @classmethod
    def after_update(cls, parent, info, instance, data):
        pass

    @classmethod
    def after_delete(cls, parent, info, instance, data):
        pass

    @ClassProperty
    @classmethod
    def Type(cls):
        return cls

    @classmethod
    def WhereInputType(cls, only=None, exclude=None, *args, **kwargs):
        return convert_model_to_input_type(
            cls._meta.model,
            input_flag="where",
            registry=cls._meta.registry,
            only=only,
            exclude=exclude,
        )

    @classmethod
    def CreateInputType(cls, only=None, exclude=None, *args, **kwargs):
        return convert_model_to_input_type(
            cls._meta.model,
            input_flag="create",
            registry=cls._meta.registry,
            only=only,
            exclude=exclude,
        )

    @classmethod
    def UpdateInputType(cls, only=None, exclude=None, *args, **kwargs):
        return convert_model_to_input_type(
            cls._meta.model,
            input_flag="update",
            registry=cls._meta.registry,
            only=only,
            exclude=exclude,
        )

    @classmethod
    def ReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    ),
                    required=True,
                ),
            }
        )
        return graphene.Field(
            cls,
            args=arguments,
            resolver=cls.read,
            *args,
            **kwargs,
        )

    @classmethod
    def read(cls, parent, info, **kwargs):
        queryset = cls._queryset_factory(info, field_ast=info.field_asts[0], node=False)
        return queryset.get()

    @classmethod
    def BatchReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    )
                ),
                "limit": graphene.Int(),
                "offset": graphene.Int(),
                "orderBy": graphene.List(graphene.String),
            }
        )
        return graphene.Field(
            node_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.batchread,
            *args,
            **kwargs,
        )

    @classmethod
    def batchread(cls, parent, info, related_field=None, **kwargs):

        if related_field is not None:
            try:
                queryset = parent.__getattr__(related_field).all()
            except:
                queryset = parent.__getattribute__(related_field).all()
        else:
            queryset = cls._queryset_factory(
                info, field_ast=info.field_asts[0], fragments=info.fragments, node=True
            )

        start = kwargs.get("offset", 0)
        limit = kwargs.get("limit", cls._meta.max_limit)
        if limit is not None and cls._meta.max_limit is not None:
            if limit > cls._meta.max_limit:
                limit = cls._meta.max_limit
        if limit is not None:
            end = start + limit
        else:
            end = None
        return {"count": queryset.count(), "data": queryset[start:end]}

    @classmethod
    def mutateItem(cls, parent, info, instance, data):
        model_fields = get_model_fields(cls._meta.model, to_dict=True)
        for key, value in data.items():
            try:
                model_field = model_fields[key]
            except KeyError:
                continue
            if isinstance(
                model_field, (OneToOneRel, ManyToOneRel, ManyToManyField, ManyToManyRel)
            ):
                pass
            elif isinstance(model_field, (ForeignKey, OneToOneField)):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                if "create" in value.keys():
                    try:
                        related_instance = related_type.create(
                            parent, info, value["create"]
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create")
                    instance.__setattr__(key, related_instance)
                elif "connect" in value.keys():
                    related_instance = (
                        related_type.get_queryset(parent, info)
                        .filter(apply_where(value["connect"]))
                        .distinct()
                        .get()
                    )
                    instance.__setattr__(key, related_instance)
            else:
                instance.__setattr__(key, value)
        instance.full_clean()
        instance.save()
        for key, value in data.items():
            try:
                model_field = model_fields[key]
            except KeyError:
                continue
            if isinstance(model_field, OneToOneRel):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                if "create" in value.keys():
                    try:
                        related_type.create(
                            parent,
                            info,
                            value["create"],
                            field=model_field.remote_field,
                            parent_instance=instance,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create")
                elif "connect" in value.keys():
                    try:
                        related_type.update(
                            parent,
                            info,
                            value["connect"],
                            {},
                            field=model_field.remote_field,
                            parent_instance=instance,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".connect")
            elif isinstance(model_field, ManyToOneRel):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                for i, create_input in enumerate(value.get("create", [])):
                    try:
                        related_type.create(
                            parent,
                            info,
                            create_input,
                            field=model_field.remote_field,
                            parent_instance=instance,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create." + str(i))
                for i, connect_input in enumerate(value.get("connect", [])):
                    try:
                        related_type.update(
                            parent,
                            info,
                            connect_input,
                            {},
                            field=model_field.remote_field,
                            parent_instance=instance,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(
                            e, key + ".connect." + str(i)
                        )
                for i, disconnect_input in enumerate(value.get("disconnect", [])):
                    try:
                        related_type.update(
                            parent,
                            info,
                            disconnect_input,
                            {},
                            field=model_field.remote_field,
                            parent_instance=None,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(
                            e, key + ".disconnect." + str(i)
                        )
                for i, delete_where_input in enumerate(value.get("delete", [])):
                    try:
                        related_type.delete(parent, info, delete_where_input)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete." + str(i))

            elif isinstance(model_field, (ManyToManyField, ManyToManyRel)):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                q = related_type.get_queryset(parent, info)
                addItems = []
                disconnectItems = []
                for i, create_input in enumerate(value.get("create", [])):
                    try:
                        addItems.append(related_type.create(parent, info, create_input))
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create." + str(i))
                for i, connect_input in enumerate(value.get("connect", [])):
                    try:
                        related_instance = (
                            q.filter(apply_where(connect_input)).distinct().get()
                        )
                        addItems.append(related_instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(
                            e, key + ".connect." + str(i)
                        )
                for i, disconnect_input in enumerate(value.get("disconnect", [])):
                    try:
                        related_instance = (
                            q.filter(apply_where(disconnect_input)).distinct().get()
                        )
                        disconnectItems.append(related_instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(
                            e, key + ".disconnect." + str(i)
                        )
                for i, delete_where_input in enumerate(value.get("delete", [])):
                    try:
                        related_type.delete(parent, info, delete_where_input)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete." + str(i))

                getattr(instance, key).add(*addItems)
                getattr(instance, key).remove(*disconnectItems)
        return instance

    @classmethod
    def CreateField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "input": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model,
                        input_flag="create",
                        registry=cls._meta.registry,
                    ),
                    required=True,
                )
            }
        )

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.create_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def create_resolver(cls, parent, info, **kwargs):
        try:
            with transaction.atomic():
                instance = cls.create(parent, info, kwargs["input"])
            return {"result": instance, "ok": True, "errors": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

    @classmethod
    def create(cls, parent, info, data, field=None, parent_instance=None):
        instance = cls._meta.model()
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
        cls.before_mutate(parent, info, instance, data)
        cls.before_create(parent, info, instance, data)
        cls.mutateItem(parent, info, instance, data)
        cls.after_create(parent, info, instance, data)
        cls.after_mutate(parent, info, instance, data)
        result_field_ast = get_field_ast_by_path(info, ["result"])
        return cls._instance_to_queryset(info, instance, result_field_ast).get()

    @classmethod
    def UpdateField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "input": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model,
                        input_flag="update",
                        registry=cls._meta.registry,
                    ),
                    required=True,
                ),
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    ),
                    required=True,
                ),
            }
        )

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.update_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def update_resolver(cls, parent, info, **kwargs):
        try:
            with transaction.atomic():
                instance = cls.update(parent, info, kwargs["where"], kwargs["input"])
            return {"result": instance, "ok": True, "error": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

    @classmethod
    def update(cls, parent, info, where, data, field=None, parent_instance=None):
        instance = (
            cls.get_queryset(parent, info).filter(apply_where(where)).distinct().get()
        )
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
        cls.before_mutate(parent, info, instance, data)
        cls.before_update(parent, info, instance, data)
        cls.mutateItem(parent, info, instance, data)
        cls.after_update(parent, info, instance, data)
        cls.after_mutate(parent, info, instance, data)
        result_field_ast = get_field_ast_by_path(info, ["result"])
        return cls._instance_to_queryset(info, instance, result_field_ast).get()

    @classmethod
    def DeleteField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    ),
                    required=True,
                ),
            }
        )

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.delete_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def delete_resolver(cls, parent, info, **kwargs):
        try:
            instance = cls.delete(parent, info, kwargs["where"])
            return {"result": None, "ok": True, "error": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

    @classmethod
    def delete(cls, parent, info, where):
        instance = (
            cls.get_queryset(parent, info).filter(apply_where(where)).distinct().get()
        )
        cls.before_mutate(parent, info, instance, {})
        cls.before_delete(parent, info, instance, {})
        instance.delete()
        cls.after_delete(parent, info, instance, {})
        cls.after_mutate(parent, info, instance, {})
        return instance

    @classmethod
    def CreatedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    )
                ),
            }
        )
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.created_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def created_resolver(cls, parent, info, **kwargs):
        def eventFilter(event):
            if event.operation == CREATED and isinstance(
                event.instance, cls._meta.model
            ):
                return (
                    cls.get_queryset(parent, info).filter(pk=event.instance.pk).exists()
                )

        return parent.filter(eventFilter).map(
            lambda event: cls._instance_to_queryset(
                info, event.instance, info.field_asts[0]
            ).get()
        )

    @classmethod
    def UpdatedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    )
                ),
            }
        )
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.updated_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def updated_resolver(cls, parent, info, **kwargs):
        def eventFilter(event):
            if event.operation == UPDATED and isinstance(
                event.instance, cls._meta.model
            ):
                return (
                    cls.get_queryset(parent, info)
                    .filter(apply_where(kwargs.get("where", {})))
                    .filter(pk=event.instance.pk)
                    .exists()
                )

        return parent.filter(eventFilter).map(
            lambda event: cls._instance_to_queryset(
                info, event.instance, info.field_asts[0]
            ).get()
        )

    @classmethod
    def DeletedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    )
                ),
            }
        )
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.deleted_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def deleted_resolver(cls, parent, info, **kwargs):
        pk_list = [
            pk
            for pk in cls.get_queryset(parent, info)
            .filter(apply_where(kwargs.get("where", {})))
            .values_list("pk", flat=True)
        ]

        def eventFilter(event):
            nonlocal pk_list
            ret = False
            if isinstance(event.instance, cls._meta.model):
                if event.operation == DELETED:
                    ret = event.instance.pk in pk_list
                pk_list = [
                    pk
                    for pk in cls.get_queryset(parent, info)
                    .filter(apply_where(kwargs.get("where", {})))
                    .values_list("pk", flat=True)
                ]
            return ret

        return parent.filter(eventFilter).map(lambda event: event.instance)
