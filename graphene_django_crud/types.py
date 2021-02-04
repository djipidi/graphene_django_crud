# -*- coding: utf-8 -*-

from collections import OrderedDict
import graphene
from graphene.types.base import BaseOptions
from graphene_django.types import ErrorType

from .utils import get_related_model, field_to_relation_type
from .base_types import mutation_factory_type, node_factory_type

from graphene_django.compat import ArrayField, HStoreField, RangeField, JSONField
from graphene_django.utils import import_single_dispatch

from django.db import models, transaction

from .converter import convert_model_to_input_type, construct_fields
from .registry import get_global_registry, Registry

from django.db.models import Q

from graphene_subscriptions.events import CREATED, UPDATED, DELETED

from graphene.types.utils import yank_fields_from_attrs


from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
    GenericRel,
)
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete 
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

def get_paths(d):
    q = [(d, [])]
    while q:
        n, p = q.pop(0)
        yield p
        if isinstance(n, dict):
            for k, v in n.items():
                q.append((v, p+[k]))

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
        if not isinstance(v,dict):
            args["__".join(path).replace("__equals","")] = v
    return args


DEFAULT_OFFSET = 0
DEFAULT_LIMIT =  100


def apply_where(where):

    AND = Q()
    OR =  Q()
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


class DjangoGrapheneCRUDOptions(BaseOptions):
    model = None

    only_fields = "__all__"
    exclude_fields = ()

    input_only_fields = "__all__"
    input_exclude_fields = ()

    interfaces = ()

    registry=None,


class DjangoGrapheneCRUD(graphene.ObjectType):
    """
        Mutation, query Type Definition
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model = None,
        only_fields="__all__",
        exclude_fields=(),
        input_only_fields = "__all__",
        input_exclude_fields = (),
        description="",
        registry=None,
        skip_registry=False,
        **options,
    ):

        if not model:
            raise Exception(
                "model is required on all DjangoGrapheneCRUD"
            )

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            "The attribute registry in {} needs to be an instance of "
            'Registry, received "{}".'
        ).format(cls.__name__, registry)

        description = description or "type for {} model".format(
            model.__name__
        )


        fields = yank_fields_from_attrs(
            construct_fields(
                model, registry, only_fields, exclude_fields
            ),
            _as=graphene.Field,
        )


        _meta = DjangoGrapheneCRUDOptions(cls)
        _meta.model = model
        _meta.fields = fields
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields

        _meta.input_only_fields = input_only_fields
        _meta.input_exclude_fields = input_exclude_fields

        _meta.registry = registry


        super(DjangoGrapheneCRUD, cls).__init_subclass_with_meta__(
            _meta=_meta, description=description, **options
        )

        if not skip_registry:
            registry.register_django_type(cls)

    @classmethod
    def generate_signals(cls):
        post_save.connect(post_save_subscription, sender=cls._meta.model)
        post_delete.connect(post_delete_subscription, sender=cls._meta.model)

    @classmethod
    def get_queryset(cls, root, info, **kwargs):
        return cls._meta.model.objects.all()

    @classmethod
    def before_mutate(cls, root, info, instance, data):
        pass

    @classmethod
    def before_create(cls, root, info, instance, data):
        pass

    @classmethod
    def before_update(cls, root, info, instance, data):
        pass

    @classmethod
    def before_delete(cls, root, info, instance, data):
        pass

    @classmethod
    def after_mutate(cls, root, info, instance, data):
        pass

    @classmethod
    def after_create(cls, root, info, instance, data):
        pass

    @classmethod
    def after_update(cls, root, info, instance, data):
        pass

    @classmethod
    def after_delete(cls, root, info, instance, data):
        pass

    @ClassProperty
    @classmethod
    def Type(cls):
        return cls


    @classmethod
    def ReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(
                convert_model_to_input_type(cls._meta.model, input_flag="where_with_operator", registry=cls._meta.registry),
                required=True
            ),
        })
        return graphene.Field(
            cls,
            args = arguments,
            resolver=cls.read,
            *args,
            **kwargs,
        )

    @classmethod
    def read(cls, root, info, **kwargs):
        return cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).get()



    @classmethod
    def BatchReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="where_with_operator", registry=cls._meta.registry)),
            "limit": graphene.Int(),
            "offset" : graphene.Int(),
            "orderBy" : graphene.List(graphene.String)
        })
        return graphene.Field(
            node_factory_type(cls, registry=cls._meta.registry),
            args = arguments,
            resolver=cls.batchread,
            *args,
            **kwargs,
        )

    @classmethod
    def batchread(cls, root, info, related_field=None, **kwargs):
        
        if related_field is not None:
            try:
                queryset =  cls.get_queryset(root, info) & root.__getattr__(related_field).all()
            except:
                queryset =  cls.get_queryset(root, info) & root.__getattribute__(related_field).all()
        else:
            queryset = cls.get_queryset(root, info)
        queryset = queryset.filter(apply_where(kwargs.get("where", {})))
        if "orderBy" in kwargs.keys():
            queryset = queryset.order_by(*kwargs.get("orderBy", []))
        return {
            'count' : queryset.count(),
            'data' : queryset \
                [kwargs.get("offset", DEFAULT_OFFSET) : kwargs.get("limit", DEFAULT_LIMIT) + kwargs.get("offset", DEFAULT_OFFSET)]
        }

    @classmethod
    def mutateItem(cls, root, info, instance, data):
        for key, value in data.items():
            if field_to_relation_type(cls._meta.model, key) == "MANY":
                pass
            elif field_to_relation_type(cls._meta.model, key) == "ONE":
                relatedModel = get_global_registry().get_type_for_model(
                    get_related_model(getattr(cls._meta.model, key).field)
                )
                q = relatedModel.get_queryset(root, info)
                if value.get("create", None):
                    instance.__setattr__(key, relatedModel.create(root, info, value["create"]) )
                if value.get("connect", None):
                    instance.__setattr__(key, q.get(apply_where(value["connect"])) )
            else:
                instance.__setattr__(key, value)
        instance.save()
        for key, value in data.items():
            if field_to_relation_type(cls._meta.model, key) == "MANY":
                relatedModel = get_global_registry().get_type_for_model(
                    get_related_model(getattr(cls._meta.model, key).field)
                )
                q = relatedModel.get_queryset(root, info)
                addItems = []
                disconnectItems = []
                for create_input in value.get("create", []):
                    addItems.append( relatedModel.create(root, info, create_input) )
                for connect_input in value.get("connect", []):
                    addItems.append(q.get(apply_where(connect_input)))
                for disconnect_input in value.get("disconnect", []):
                    disconnectItems.append(q.get(apply_where(disconnect_input)))
                for remove_where_input in value.get("remove", []):
                    relatedModel.delete(root, info, remove_where_input)

                getattr(instance, key).add(*addItems)
                getattr(instance, key).remove(*disconnectItems)
        return instance

    @classmethod
    def CreateField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update(
            {"input": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="create", registry=cls._meta.registry), required=True)}
        )

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args = arguments,
            resolver=cls.create_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def create_resolver(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                instance = cls.create(root, info, kwargs["input"])
            return {
                "result" : instance,
                "ok" : True,
                "errors" : []
            }
        except Exception as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : ErrorType.from_errors({"input": [type(e).__name__ + ": " + str(e)]})
            }

    @classmethod
    def create(cls, root, info, data):
        instance = cls._meta.model()
        cls.before_mutate(root, info, instance, data)
        cls.before_create(root, info, instance, data)
        cls.mutateItem(root, info, instance, data)
        cls.after_create(root, info, instance, data)
        cls.after_mutate(root, info, instance, data)
        return instance





    @classmethod
    def UpdateField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update({
            "input": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="update", registry=cls._meta.registry), required=True),
            "where": graphene.Argument(
                convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry),
                required=True),
        })

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.update_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def update_resolver(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                instance = cls.update(root, info, kwargs["where"], kwargs["input"])
            return {
                "result" : instance,
                "ok" : True,
                "error" : []
            }
        except Exception as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : ErrorType.from_errors({"input": [type(e).__name__ + ": " + str(e)]})
            }

    @classmethod
    def update(cls, root, info, where, data):
        instance = cls.get_queryset(root, info).get(apply_where(where))
        cls.before_mutate(root, info, instance, data)
        cls.before_update(root, info, instance, data)
        cls.mutateItem(root, info, instance, data)
        cls.after_update(root, info, instance, data)
        cls.after_mutate(root, info, instance, data)
        return instance



    @classmethod
    def DeleteField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(
                convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry),
                required=True
            ),
        })

        return graphene.Field(
            mutation_factory_type(cls, registry=cls._meta.registry),
            args=arguments,
            resolver=cls.delete_resolver,
            *args,
            **kwargs
        )

    @classmethod
    def delete_resolver(cls, root, info, **kwargs):
        try:
            instance = cls.delete(root, info, kwargs["where"])
            return {
                "result" : None,
                "ok" : True,
                "error" : []
            }
        except Exception as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : ErrorType.from_errors({"input": [type(e).__name__ + ": " + str(e)]})
            }

    @classmethod
    def delete(cls, root, info, where):
        instance = cls.get_queryset(root, info).get(apply_where(where))
        cls.before_mutate(root, info, instance, {})
        cls.before_delete(root, info, instance, {})
        instance.delete()
        cls.after_delete(root, info, instance, {})
        cls.after_mutate(root, info, instance, {})
        return instance

    @classmethod
    def CreatedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry)),
        })
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.created_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def created_resolver(cls, root, info, **kwargs):
        def eventFilter(event):
            if event.operation == CREATED and isinstance(event.instance, cls._meta.model):
                return cls.get_queryset(root, info).filter(pk=event.instance.pk).exists()

        return root.filter(
            eventFilter
        ).map(lambda event: event.instance)
        
    @classmethod
    def UpdatedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry)),
        })
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.updated_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def updated_resolver(cls, root, info, **kwargs):
        def eventFilter(event):
            if event.operation == UPDATED and isinstance(event.instance, cls._meta.model):
                return cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).filter(pk=event.instance.pk).exists()
        return root.filter(
            eventFilter
        ).map(lambda event: event.instance)


    @classmethod
    def DeletedField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry)),
        })
        return graphene.Field(
            cls.Type,
            args=arguments,
            resolver=cls.deleted_resolver,
            *args,
            **kwargs,
        )

    @classmethod
    def deleted_resolver(cls, root, info, **kwargs):
        pk_list = [pk for pk in cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).values_list("pk", flat=True)]
        def eventFilter(event):
            nonlocal pk_list
            ret = False
            if isinstance(event.instance, cls._meta.model):
                if event.operation == DELETED:
                    ret = event.instance.pk in pk_list
                pk_list = [pk for pk in cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).values_list("pk", flat=True)]
            return ret
        return root.filter(
            eventFilter
        ).map(lambda event: event.instance)