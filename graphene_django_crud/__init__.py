# -*- coding: utf-8 -*-
from .types import DjangoGrapheneCRUD, DjangoCRUDObjectType, resolver_hints
from .utils import where_input_to_Q, order_by_input_to_args
from .base_types import DefaultConnection, EmptyDefaultConnection

# Horrific monkey patch
import django.utils.encoding
django.utils.encoding.force_text = django.utils.encoding.force_str

__version__ = "1.3.4"

__all__ = (
    "__version__",
    "DjangoCRUDObjectType",
    "DjangoGrapheneCRUD",
    "resolver_hints",
    "where_input_to_Q",
    "order_by_input_to_args",
    "DefaultConnection",
    "EmptyDefaultConnection",
)
