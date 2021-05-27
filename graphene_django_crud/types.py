# -*- coding: utf-8 -*-

from collections import OrderedDict
import graphene
from graphene.types.base import BaseOptions
from graphql.language.ast import FragmentSpread, InlineFragment

from .utils import (
    get_model_fields,
    parse_arguments_ast,
    get_field_ast_by_path,
    resolve_argument,
    get_type_field,
    where_input_to_Q,
    order_by_input_to_args,
    error_data_from_validation_error,
    validation_error_with_suffix,
)
from .base_types import mutation_factory_type, node_factory_type

from django.db.models import Prefetch
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

    where_only_fields = "__all__"
    where_exclude_fields = ()

    order_by_only_fields = "__all__"
    order_by_exclude_fields = ()

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
        where_only_fields="__all__",
        where_exclude_fields=(),
        order_by_only_fields="__all__",
        order_by_exclude_fields=(),
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

        _meta.where_only_fields = where_only_fields
        _meta.where_exclude_fields = where_exclude_fields

        _meta.order_by_only_fields = order_by_only_fields
        _meta.order_by_exclude_fields = order_by_exclude_fields

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
        if "where" in arguments.keys():
            where = resolve_argument(cls.WhereInputType(), arguments.get("where", {}))
            queryset = queryset.filter(where_input_to_Q(where))
        if "orderBy" in arguments.keys() or "order_by" in arguments.keys():
            order_by = arguments.get("orderBy", [])
            if isinstance(order_by, dict):
                order_by = [order_by]
            order_by = resolve_argument(cls.OrderByInputType(), order_by)
            queryset = queryset.order_by(*order_by_input_to_args(order_by))
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
        computed_field_hints = {}
        for field_name, field in cls._meta.fields.items():
            if field_name in model_fields.keys():
                continue
            if field.resolver is None:
                resolver = cls.__dict__.get("resolve_" + field_name, None)
            else:
                resolver = field.resolver
            if resolver is not None and hasattr(resolver, "have_resolver_hints"):
                computed_field_hints[field_name] = {
                    "only": resolver.only,
                    "select_related": resolver.select_related,
                    "prefetch_related": [],
                }

        for field in selection_set.selections:

            if field.name.value.startswith("__"):
                continue

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
                real_name = get_type_field(cls, field.name.value)[0]
                try:
                    model_field = model_fields[real_name]
                except KeyError:
                    try:
                        computed_field = computed_field_hints[real_name]
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
                        ret["select_related"].append(new_suffix + real_name)
                        new_ret = related_type._queryset_factory_analyze(
                            info,
                            field.selection_set,
                            node=False,
                            suffix=new_suffix + real_name,
                        )
                        ret = fusion_ret(ret, new_ret)
                    elif isinstance(
                        model_field, (ManyToManyField, ManyToManyRel, ManyToOneRel)
                    ):
                        ret["prefetch_related"].append(
                            Prefetch(
                                new_suffix + real_name,
                                queryset=related_type._queryset_factory(
                                    info, field_ast=field, node=True
                                ),
                            )
                        )

                else:
                    ret["only"].append(new_suffix + real_name)
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
    def OrderByInputType(cls, only=None, exclude=None, *args, **kwargs):
        return convert_model_to_input_type(
            cls._meta.model,
            input_flag="order_by",
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
                "orderBy": graphene.List(
                    convert_model_to_input_type(
                        cls._meta.model,
                        input_flag="order_by",
                        registry=cls._meta.registry,
                    )
                ),
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
                        .filter(where_input_to_Q(value["connect"]))
                        .distinct()
                        .get()
                    )
                    instance.__setattr__(key, related_instance)
                elif "disconnect" in value.keys():
                    instance.__setattr__(key, None)
                elif "delete" in value.keys():
                    try:
                        related_instance = getattr(instance, key)
                        related_type.delete(
                            parent, info, {"id": {"equals": related_instance.pk}}
                        )
                        instance.__setattr__(key, None)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete")
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
                elif "disconnect" in value.keys():
                    try:
                        related_instance = getattr(instance, key)

                        related_type.update(
                            parent,
                            info,
                            None,
                            {},
                            instance_pk=related_instance.pk,
                            field=model_field.remote_field,
                            parent_instance=None,
                        )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".connect")
                elif "delete" in value.keys():
                    try:
                        related_instance = getattr(instance, key)
                        related_type.delete(
                            parent, info, None, instance_pk=related_instance.pk
                        )
                        instance.__setattr__(key, None)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete")

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
                            q.filter(where_input_to_Q(connect_input)).distinct().get()
                        )
                        addItems.append(related_instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(
                            e, key + ".connect." + str(i)
                        )
                for i, disconnect_input in enumerate(value.get("disconnect", [])):
                    try:
                        related_instance = (
                            q.filter(where_input_to_Q(disconnect_input))
                            .distinct()
                            .get()
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
            instance = cls.create(parent, info, kwargs["input"])
            result_field_ast = get_field_ast_by_path(info, ["result"])
            instance = cls._instance_to_queryset(
                info, instance, result_field_ast
            ).get()
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
        return instance

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
            instance = cls.update(parent, info, kwargs["where"], kwargs["input"])
            result_field_ast = get_field_ast_by_path(info, ["result"])
            instance = cls._instance_to_queryset(
                info, instance, result_field_ast
            ).get()
            return {"result": instance, "ok": True, "error": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

    @classmethod
    def update(
        cls,
        parent,
        info,
        where,
        data,
        field=None,
        parent_instance=None,
        instance_pk=None,
    ):
        queryset = cls.get_queryset(parent, info)
        if instance_pk is not None:
            queryset = queryset.filter(pk=instance_pk)
        else:
            queryset = queryset.filter(where_input_to_Q(where)).distinct()
        instance = queryset.get()
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
        cls.before_mutate(parent, info, instance, data)
        cls.before_update(parent, info, instance, data)
        cls.mutateItem(parent, info, instance, data)
        cls.after_update(parent, info, instance, data)
        cls.after_mutate(parent, info, instance, data)
        return instance

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
    def delete(cls, parent, info, where, instance_pk=None):
        queryset = cls.get_queryset(parent, info)
        if instance_pk is not None:
            queryset = queryset.filter(pk=instance_pk)
        else:
            queryset = queryset.filter(where_input_to_Q(where)).distinct()
        instance = queryset.get()
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
                    .filter(where_input_to_Q(kwargs.get("where", {})))
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
            .filter(where_input_to_Q(kwargs.get("where", {})))
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
                    .filter(where_input_to_Q(kwargs.get("where", {})))
                    .values_list("pk", flat=True)
                ]
            return ret

        return parent.filter(eventFilter).map(lambda event: event.instance)
