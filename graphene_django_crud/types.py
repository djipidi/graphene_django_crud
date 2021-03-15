# -*- coding: utf-8 -*-

from collections import OrderedDict
import graphene
from graphene.types.base import BaseOptions
from graphene_django.types import ErrorType

from .utils import get_related_model, get_model_fields
from .base_types import mutation_factory_type, node_factory_type

from django.db import models, transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from .converter import convert_model_to_input_type, construct_fields
from .registry import get_global_registry, Registry

from graphene_subscriptions.events import CREATED, UPDATED, DELETED

from graphene.types.utils import yank_fields_from_attrs

from django.db.models.signals import post_save, post_delete, pre_delete 
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

from django.db.models import (
    ManyToOneRel,
    ManyToManyRel,
    OneToOneRel,
    ForeignKey,
    ManyToManyField,
    OneToOneField
)

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

def error_data_from_validation_error(validation_error):
    ret = []
    for field, error_list in validation_error.error_dict.items():
        messages = []
        for error in error_list:
            messages.extend(error.messages)
        ret.append({
            "field":field,
            "messages":messages
        })
    return ret

def validation_error_with_suffix(validation_error, suffix):
    error_dict = {}
    for field, error_list in validation_error.error_dict.items():
        error_dict[suffix + "." + field] = error_list
    return ValidationError(error_dict)

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

    max_limit = None

    only_fields = "__all__"
    exclude_fields = ()

    input_only_fields = "__all__"
    input_exclude_fields = ()
    input_extend_fields = ()

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
        max_limit = None,
        only_fields="__all__",
        exclude_fields=(),
        input_only_fields = "__all__",
        input_exclude_fields = (),
        input_extend_fields = (),
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
    def WhereInputType(cls, *args, **kwargs):
        return convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry)

    @classmethod
    def CreateInputType(cls, *args, **kwargs):
        return convert_model_to_input_type(cls._meta.model, input_flag="create", registry=cls._meta.registry)

    @classmethod
    def UpdateInputType(cls, *args, **kwargs):
        return convert_model_to_input_type(cls._meta.model, input_flag="update", registry=cls._meta.registry)

    @classmethod
    def ReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(
                convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry),
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
        return cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).distinct().get()



    @classmethod
    def BatchReadField(cls, *args, **kwargs):

        arguments = OrderedDict()
        arguments.update({
            "where": graphene.Argument(convert_model_to_input_type(cls._meta.model, input_flag="where", registry=cls._meta.registry)),
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
        queryset = queryset.distinct()

        start = kwargs.get("offset", 0)
        limit = kwargs.get("limit", cls._meta.max_limit)
        if limit is not  None and cls._meta.max_limit is not None:
            if limit > cls._meta.max_limit:
                limit = cls._meta.max_limit
        if limit is not None:
            end = start + limit
        else:
            end = None
        return {
            'count' : queryset.count(),
            'data' : queryset[start:end]
        }

    @classmethod
    def mutateItem(cls, root, info, instance, data):
        model_fields = get_model_fields(cls._meta.model, to_dict=True)
        for key, value in data.items():
            try:
                model_field = model_fields[key]
            except KeyError:
                continue
            if isinstance(model_field, (OneToOneRel ,ManyToOneRel, ManyToManyField, ManyToManyRel)):
                pass
            elif isinstance(model_field, (ForeignKey, OneToOneField)):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                if "create" in value.keys():
                    try:
                        related_instance = related_type.create(root, info, value["create"])
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create")
                    instance.__setattr__(key, related_instance )
                elif "connect" in value.keys():
                    related_instance = related_type.get_queryset(root, info).filter(apply_where(value["connect"])).distinct().get()
                    instance.__setattr__(key, related_instance )
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
                        related_type.create(root, info, value["create"], field=model_field.remote_field, parent_instance=instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create")
                elif "connect" in value.keys():
                    try:
                        related_type.update(root, info, value["connect"], {}, field=model_field.remote_field, parent_instance=instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".connect")
            elif isinstance(model_field, ManyToOneRel):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                for i, create_input in enumerate(value.get("create", [])):
                    try:
                        related_type.create(root, info, create_input, field=model_field.remote_field, parent_instance=instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create." + str(i))
                for i, connect_input in enumerate(value.get("connect", [])):
                    try:
                        related_type.update(root, info, connect_input, {}, field=model_field.remote_field, parent_instance=instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".connect." + str(i))
                for i, disconnect_input in enumerate(value.get("disconnect", [])):
                    try:
                        related_type.update(root, info, disconnect_input, {}, field=model_field.remote_field, parent_instance=None)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".disconnect." + str(i))
                for i, delete_where_input in enumerate(value.get("delete", [])):
                    try:
                        related_type.delete(root, info, delete_where_input)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete." + str(i))

            elif isinstance(model_field, (ManyToManyField, ManyToManyRel)):
                related_type = get_global_registry().get_type_for_model(
                    model_field.remote_field.model
                )
                q = related_type.get_queryset(root, info)
                addItems = []
                disconnectItems = []
                for i, create_input in enumerate(value.get("create", [])):
                    try:
                        addItems.append( related_type.create(root, info, create_input) )
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".create." + str(i))
                for i, connect_input in enumerate(value.get("connect", [])):
                    try:
                        related_instance = q.filter(apply_where(connect_input)).distinct().get()
                        addItems.append(related_instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".connect." + str(i))
                for i, disconnect_input in enumerate(value.get("disconnect", [])):
                    try:
                        related_instance = q.filter(apply_where(disconnect_input)).distinct().get()
                        disconnectItems.append(related_instance)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".disconnect." + str(i))
                for i, delete_where_input in enumerate(value.get("delete", [])):
                    try:
                        related_type.delete(root, info, delete_where_input)
                    except ValidationError as e:
                        raise validation_error_with_suffix(e, key + ".delete." + str(i))

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
        except ValidationError as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : error_data_from_validation_error(e)
            }

    @classmethod
    def create(cls, root, info, data, field=None, parent_instance=None):
        instance = cls._meta.model()
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
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
        except ValidationError as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : error_data_from_validation_error(e)
            }

    @classmethod
    def update(cls, root, info, where, data, field=None, parent_instance=None):
        instance = cls.get_queryset(root, info).filter(apply_where(where)).distinct().get()
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
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
        except ValidationError as e:
            return {
                "result": None,
                "ok" : False,
                "errors" : error_data_from_validation_error(e)
            }

    @classmethod
    def delete(cls, root, info, where):
        instance = cls.get_queryset(root, info).filter(apply_where(where)).distinct().get()
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
                return cls.get_queryset(root, info).filter(apply_where(kwargs.get("where", {}))).filter(pk=event.instance.pk).exists()

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