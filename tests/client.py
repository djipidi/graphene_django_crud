  
# -*- coding: utf-8 -*-
from django.test import Client as BaseClient
from django.urls import reverse
import json


class Client(BaseClient):
    url = reverse("graphql")

    def query(self, query, variables=None):
        data = {
            "query": query
        }
        if variables is not None:
            data["variables"] = json.dumps(variables)
        response = self.post(path=self.url, data=data)
        return response