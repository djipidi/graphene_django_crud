# -*- coding: utf-8 -*-
from graphene_django_crud import DjangoCRUDObjectType
import graphene
from .models import *

from graphene import relay

class TestFileType(DjangoCRUDObjectType):
    class Meta:
        model = TestFile


class Query(graphene.ObjectType):

    test_file = TestFileType.ReadField()
    test_files = TestFileType.BatchReadField()



class Mutation(graphene.ObjectType):

    test_file_create = TestFileType.CreateField()
    test_file_update = TestFileType.UpdateField()
    test_file_delete = TestFileType.DeleteField()
