# -*- coding: utf-8 -*-
import django
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from .schema import schema_no_camelcase

if django.VERSION >= (2, 0):
    from django.urls import path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path(
            "graphql", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql"
        ),
        path(
            "graphql_no_camelcase", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema_no_camelcase)), name="graphql_no_camelcase"
        ),
    ]
else:
    from django.conf.urls import url

    urlpatterns = [
        url("admin/", admin.site.urls),
        url("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql"),
        url("graphqlnocamelcase", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema_no_camelcase)), name="graphql_no_camel_case"),
    ]
