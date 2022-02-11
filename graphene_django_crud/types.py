# -*- coding: utf-8 -*-

from collections import OrderedDict
from django.utils.functional import SimpleLazyObject
from django.core.files.uploadedfile import UploadedFile
import graphene
from graphene.types.objecttype import ObjectTypeOptions
from graphene_django.utils.utils import is_valid_django_model
from graphql.language.ast import FragmentSpread, InlineFragment
from graphene.relay import Connection as RelayConnection, Node
import io
from django.core.files import File

from .fields import DjangoConnectionField, DjangoListField
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
from .base_types import mutation_factory_type, DefaultConnection

from django.db.models import Prefetch
from django.core.exceptions import ValidationError

from .converter import convert_model_to_input_type, construct_fields
from .registry import get_global_registry, Registry

from graphene_subscriptions.events import CREATED, UPDATED, DELETED

from graphene.types.utils import yank_fields_from_attrs

from django.db.models.signals import post_save, post_delete
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
    FileField,
    ImageField,
)
import warnings

from .settings import gdc_settings


def resolver_hints(select_related=[], only=[], **kwargs):
    def wrapper(f):
        f.select_related = select_related
        f.only = only
        f.have_resolver_hints = True
        return f

    return wrapper


class DjangoCRUDObjectTypeOptions(ObjectTypeOptions):
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

    validator = True
    validator_exclude = None
    validator_validate_unique = True

    connection = None
    use_connection = None
    connection_class = None

    registry = (None,)


class DjangoCRUDObjectType(graphene.ObjectType):
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
        validator=True,
        validator_exclude=None,
        validator_validate_unique=True,
        description="",
        connection=None,
        connection_class=None,
        use_connection=True,
        interfaces=(),
        registry=None,
        skip_registry=False,
        _meta=None,
        **options,
    ):
        if not model:
            raise Exception("model is required on all DjangoCRUDObjectType")

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

        use_relay = False
        if interfaces:
            use_relay = any((issubclass(interface, Node) for interface in interfaces))
            if use_relay and not use_connection:
                use_connection = True

        if use_connection and not connection:
            # We create the connection automatically
            if not connection_class:
                if use_relay:
                    connection_class = RelayConnection
                else:
                    connection_class = DefaultConnection

            connection = connection_class.create_type(
                "{}Connection".format(options.get("name") or cls.__name__), node=cls
            )

        if not _meta:
            _meta = DjangoCRUDObjectTypeOptions(cls)
        
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

        _meta.validator = validator
        _meta.validator_exclude = validator_exclude
        _meta.validator_validate_unique = validator_validate_unique

        _meta.connection = connection
        _meta.connection_class = connection_class
        _meta.use_connection = use_connection

        _meta.registry = registry

        super(DjangoCRUDObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, interfaces=interfaces, description=description, **options
        )

        if not skip_registry:
            registry.register_django_type(cls)

    @classmethod
    def _display_deprecation_warnings(cls):
        before_xxx_after_xxx_warning_message = (
            "Overload to deprecated methods {}. Replace it with {}."
        )
        if getattr(cls, "before_mutate", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("before_mutate", "mutate"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "after_mutate", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("after_mutate", "mutate"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "before_create", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("before_create", "create"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "after_create", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("after_create", "create"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "before_update", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("before_update", "update"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "after_update", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("after_update", "update"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "before_delete", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("before_delete", "delete"),
                category=DeprecationWarning,
                stacklevel=2,
            )
        if getattr(cls, "after_delete", None):
            warnings.warn(
                before_xxx_after_xxx_warning_message.format("after_delete", "delete"),
                category=DeprecationWarning,
                stacklevel=2,
            )

    @classmethod
    def _queryset_factory(cls, info, field_ast=None, is_connection=True, **kwargs):
        queryset = cls.get_queryset(None, info)
        arguments = parse_arguments_ast(
            field_ast.arguments, variable_values=info.variable_values
        )

        queryset_factory = cls._queryset_factory_analyze(
            info, field_ast.selection_set, is_connection=is_connection
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
    def _queryset_factory_analyze(
        cls, info, selection_set, is_connection=True, suffix=""
    ):
        def fusion_ret(a, b):

            [
                a["select_related"].append(x)
                for x in b["select_related"]
                if x not in a["select_related"]
            ]
            [a["prefetch_related"].append(x) for x in b["prefetch_related"]]
            [a["only"].append(x) for x in b["only"] if x not in a["only"]]
            return a

        if is_connection and not cls._meta.use_connection:
            is_connection = False

        if suffix == "":
            new_suffix = ""
        else:
            new_suffix = suffix + "__"

        ret = {"select_related": [], "only": [new_suffix + cls._meta.model._meta.pk.name], "prefetch_related": []}

        model_fields, computed_field_hints = cls._get_fields()

        for field in selection_set.selections:

            if isinstance(field, FragmentSpread):
                new_ret = cls._queryset_factory_analyze(
                    info,
                    info.fragments[field.name.value].selection_set,
                    suffix=suffix,
                    is_connection=is_connection,
                )
                ret = fusion_ret(ret, new_ret)
                continue

            if isinstance(field, InlineFragment):
                if field.type_condition.name.value == cls.__name__:
                    new_ret = cls._queryset_factory_analyze(
                        info,
                        field.selection_set,
                        suffix=suffix,
                        is_connection=is_connection,
                    )
                    ret = fusion_ret(ret, new_ret)
                continue

            if field.name.value.startswith("__"):
                continue

            if is_connection:
                if field.name.value in [
                    gdc_settings.DEFAULT_CONNECTION_NODES_FIELD_NAME,
                    "node",
                ]:
                    new_ret = cls._queryset_factory_analyze(
                        info,
                        field.selection_set,
                        suffix=new_suffix,
                        is_connection=False,
                    )
                    ret = fusion_ret(ret, new_ret)

                elif field.name.value in ["edges"]:
                    new_ret = cls._queryset_factory_analyze(
                        info,
                        field.selection_set,
                        suffix=new_suffix,
                        is_connection=True,
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
                    if isinstance(
                        model_field,
                        (
                            OneToOneField,
                            OneToOneRel,
                            ForeignKey,
                            ManyToManyField,
                            ManyToManyRel,
                            ManyToOneRel,
                        ),
                    ):
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
                                is_connection=False,
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
                                        info, field_ast=field, is_connection=True
                                    ),
                                )
                            )
                    elif isinstance(model_field, FileField):
                        ret["only"].append(new_suffix + real_name)
                else:
                    ret["only"].append(new_suffix + real_name)
        return ret

    @classmethod
    def _get_fields(cls):
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
        return model_fields, computed_field_hints

    @classmethod
    def _instance_to_queryset(cls, info, instance, field_ast):
        queryset = cls._queryset_factory(info, field_ast=field_ast, is_connection=False)
        queryset = queryset.filter(pk=instance.pk)
        return queryset

    @classmethod
    def _create(cls, parent, info, data, field=None, parent_instance=None):
        instance = cls._meta.model()
        if field is not None:
            instance.__setattr__(field.name, parent_instance)
        return cls.mutate(parent, info, instance, data, operation_flag="create")

    @classmethod
    def _update(
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
        return cls.mutate(parent, info, instance, data, operation_flag="update")

    @classmethod
    def _delete(cls, parent, info, where, instance_pk=None):
        queryset = cls.get_queryset(parent, info)
        if instance_pk is not None:
            queryset = queryset.filter(pk=instance_pk)
        else:
            queryset = queryset.filter(where_input_to_Q(where)).distinct()
        instance = queryset.get()
        return cls.mutate(parent, info, instance, {}, operation_flag="delete")

    @classmethod
    def _update_or_create(cls, parent, info, instance, data):
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
                cls._nested_mutate_Fk_O2OF(
                    parent, info, instance, key, value, model_field
                )
            elif isinstance(model_field, (FileField, ImageField)):
                if "upload" in value.keys():
                    instance.__setattr__(
                        key,
                        File(
                            value["upload"].file,
                            value.get("filename", value["upload"].name),
                        ),
                    )
                else:
                    instance.__setattr__(
                        key, File(io.BytesIO(value["content"]), value["filename"])
                    )
            else:
                instance.__setattr__(key, value)
        if cls._meta.validator:
            instance.full_clean(
                exclude=cls._meta.validator_exclude,
                validate_unique=cls._meta.validator_validate_unique,
            )
        instance.save()
        for key, value in data.items():
            try:
                model_field = model_fields[key]
            except KeyError:
                continue
            if isinstance(model_field, OneToOneRel):
                cls._nested_mutate_O2OR(parent, info, instance, key, value, model_field)

            elif isinstance(model_field, ManyToOneRel):
                cls._nested_mutate_M2OR(parent, info, instance, key, value, model_field)

            elif isinstance(model_field, (ManyToManyField, ManyToManyRel)):
                cls._nested_mutate_M2M(parent, info, instance, key, value, model_field)
        return instance

    @classmethod
    def _nested_mutate_M2M(cls, parent, info, instance, key, value, model_field):
        related_type = get_global_registry().get_type_for_model(
            model_field.remote_field.model
        )
        q = related_type.get_queryset(parent, info)
        addItems = []
        disconnectItems = []
        for i, create_input in enumerate(value.get("create", [])):
            try:
                addItems.append(related_type._create(parent, info, create_input))
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".create." + str(i))
        for i, connect_input in enumerate(value.get("connect", [])):
            try:
                related_instance = (
                    q.filter(where_input_to_Q(connect_input)).distinct().get()
                )
                addItems.append(related_instance)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".connect." + str(i))
        for i, disconnect_input in enumerate(value.get("disconnect", [])):
            try:
                related_instance = (
                    q.filter(where_input_to_Q(disconnect_input)).distinct().get()
                )
                disconnectItems.append(related_instance)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".disconnect." + str(i))
        for i, delete_where_input in enumerate(value.get("delete", [])):
            try:
                related_type._delete(parent, info, delete_where_input)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".delete." + str(i))
        getattr(instance, key).add(*addItems)
        getattr(instance, key).remove(*disconnectItems)

    @classmethod
    def _nested_mutate_M2OR(cls, parent, info, instance, key, value, model_field):
        related_type = get_global_registry().get_type_for_model(
            model_field.remote_field.model
        )
        for i, create_input in enumerate(value.get("create", [])):
            try:
                related_type._create(
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
                related_type._update(
                    parent,
                    info,
                    connect_input,
                    {},
                    field=model_field.remote_field,
                    parent_instance=instance,
                )
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".connect." + str(i))
        for i, disconnect_input in enumerate(value.get("disconnect", [])):
            try:
                related_type._update(
                    parent,
                    info,
                    disconnect_input,
                    {},
                    field=model_field.remote_field,
                    parent_instance=None,
                )
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".disconnect." + str(i))
        for i, delete_where_input in enumerate(value.get("delete", [])):
            try:
                related_type._delete(parent, info, delete_where_input)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".delete." + str(i))

    @classmethod
    def _nested_mutate_O2OR(cls, parent, info, instance, key, value, model_field):
        related_type = get_global_registry().get_type_for_model(
            model_field.remote_field.model
        )
        if "create" in value.keys():
            try:
                related_type._create(
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
                related_type._update(
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
                related_type._update(
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
                related_type._delete(parent, info, {}, instance_pk=related_instance.pk)
                instance.__setattr__(key, None)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".delete")

    @classmethod
    def _nested_mutate_Fk_O2OF(cls, parent, info, instance, key, value, model_field):
        related_type = get_global_registry().get_type_for_model(
            model_field.remote_field.model
        )
        if "create" in value.keys():
            try:
                related_instance = related_type._create(parent, info, value["create"])
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
                related_type._delete(parent, info, {}, instance_pk=related_instance.pk)
                instance.__setattr__(key, None)
            except ValidationError as e:
                raise validation_error_with_suffix(e, key + ".delete")

    @classmethod
    def generate_signals(cls):
        post_save.connect(post_save_subscription, sender=cls._meta.model)
        post_delete.connect(post_delete_subscription, sender=cls._meta.model)

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        return cls._meta.model.objects.all()

    @classmethod
    def mutate(cls, parent, info, instance, data, operation_flag=None, *args, **kwargs):
        if getattr(cls, "before_mutate", None):
            cls.before_mutate(parent, info, instance, data)
        if operation_flag == "create":
            instance = cls.create(parent, info, instance, data, *args, **kwargs)
        if operation_flag == "update":
            instance = cls.update(parent, info, instance, data, *args, **kwargs)
        if operation_flag == "delete":
            instance = cls.delete(parent, info, instance, data, *args, **kwargs)
        if getattr(cls, "after_mutate", None):
            cls.after_mutate(parent, info, instance, data)
        return instance

    @classmethod
    def create(cls, parent, info, instance, data, *args, **kwargs):
        if getattr(cls, "before_create", None):
            cls.before_create(parent, info, instance, data)
        instance = cls._update_or_create(parent, info, instance, data)
        if getattr(cls, "after_create", None):
            cls.after_create(parent, info, instance, data)
        return instance

    @classmethod
    def update(cls, parent, info, instance, data, *args, **kwargs):
        if getattr(cls, "before_update", None):
            cls.before_update(parent, info, instance, data)
        instance = cls._update_or_create(parent, info, instance, data)
        if getattr(cls, "after_update", None):
            cls.after_update(parent, info, instance, data)
        return instance

    @classmethod
    def delete(cls, parent, info, instance, data, *args, **kwargs):
        if getattr(cls, "before_delete", None):
            cls.before_delete(parent, info, instance, data)
        instance.delete()
        if getattr(cls, "after_delete", None):
            cls.after_delete(parent, info, instance, data)
        return instance

    @classmethod
    def get_node(cls, info, id):
        try:
            return cls._queryset_factory(
                info, field_ast=info.field_asts[0], is_connection=False
            ).get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None

    def resolve_id(self, info):
        return self.pk

    @classmethod
    def is_type_of(cls, root, info):
        if isinstance(root, SimpleLazyObject):
            root._setup()
            root = root._wrapped
        if isinstance(root, cls):
            return True
        if not is_valid_django_model(type(root)):
            raise Exception(('Received incompatible instance "{}".').format(root))

        if cls._meta.model._meta.proxy:
            model = root._meta.model
        else:
            model = root._meta.model._meta.concrete_model

        return model == cls._meta.model

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
        queryset = cls._queryset_factory(
            info, field_ast=info.field_asts[0], is_connection=False
        )
        return queryset.get()

    @classmethod
    def BatchReadField(cls, *args, **kwargs):
        kwargs.update(
            {
                "where": graphene.Argument(
                    convert_model_to_input_type(
                        cls._meta.model, input_flag="where", registry=cls._meta.registry
                    )
                ),
                "order_by": graphene.List(
                    convert_model_to_input_type(
                        cls._meta.model,
                        input_flag="order_by",
                        registry=cls._meta.registry,
                    )
                ),
            }
        )
        if cls._meta.connection:
            return DjangoConnectionField(cls, *args, **kwargs)
        return DjangoListField(cls, *args, **kwargs)

    @classmethod
    def batchread(cls, parent, info, related_field=None, **kwargs):
        if parent is not None:
            try:
                queryset = parent.__getattr__(related_field).all()
            except:
                queryset = parent.__getattribute__(related_field).all()
        else:
            queryset = cls._queryset_factory(
                info,
                field_ast=info.field_asts[0],
                fragments=info.fragments,
                is_connection=True,
            )

        return queryset

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
            instance = cls._create(parent, info, kwargs["input"])
            result_field_ast = get_field_ast_by_path(info, ["result"])
            if result_field_ast is not None:
                instance = cls._instance_to_queryset(info, instance, result_field_ast).get()
            else:
                instance = None
            return {"result": instance, "ok": True, "errors": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

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
            instance = cls._update(parent, info, kwargs["where"], kwargs["input"])
            result_field_ast = get_field_ast_by_path(info, ["result"])
            if result_field_ast is not None:
                instance = cls._instance_to_queryset(info, instance, result_field_ast).get()
            else:
                instance = None
            return {"result": instance, "ok": True, "error": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

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
            instance = cls._delete(parent, info, kwargs["where"])
            return {"result": None, "ok": True, "error": []}
        except ValidationError as e:
            return {
                "result": None,
                "ok": False,
                "errors": error_data_from_validation_error(e),
            }

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
            cls,
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
            cls,
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
            cls,
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


class DjangoGrapheneCRUD(DjangoCRUDObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        warnings.warn(
            'DjangoGrapheneCRUD class has been renamed to DjangoCRUDObjectType, so the name "DjangoGrapheneCRUD" is deprecated.',
            category=DeprecationWarning,
            stacklevel=2,
        )
        super(DjangoGrapheneCRUD, cls).__init_subclass_with_meta__(**options)
