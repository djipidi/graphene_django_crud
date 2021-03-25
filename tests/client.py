# -*- coding: utf-8 -*-
from django.test import Client as BaseClient
from django.urls import reverse
import json


class Client(BaseClient):
    url = reverse("graphql")
    url_no_camelcase = reverse("graphql_no_camelcase")

    def query(self, query, variables=None, no_camelcase=False):
        data = {"query": query}
        if variables is not None:
            data["variables"] = json.dumps(variables)
        response = self.post(path=self.url if not no_camelcase else self.url_no_camelcase, data=data)
        return response
