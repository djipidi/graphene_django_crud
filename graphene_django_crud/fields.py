# -*- coding: utf-8 -*-
from functools import partial

from django.db.models.query import QuerySet

from graphene import NonNull

from graphene.types import Field, List

from .base_types import node_factory_type


class DjangoListField(Field):
    def __init__(self, _type, *args, **kwargs):

        if isinstance(_type, NonNull):
            _type = _type.of_type
        self.django_type = _type
        
        # Django would never return a Set of None  vvvvvvv
        super(DjangoListField, self).__init__(NonNull(node_factory_type(_type)), *args, **kwargs)

        # assert issubclass(
        #     self._underlying_type, DjangoObjectType
        # ), "DjangoListField only accepts DjangoObjectType types"

    @property
    def _underlying_type(self):
        _type = self._type
        while hasattr(_type, "of_type"):
            _type = _type.of_type
        return _type


    def get_resolver(self, parent_resolver):

        return self.django_type.batchread