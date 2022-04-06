# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins

# https://github.com/djipidi/graphene_django_crud/issues/8


gql_1 = """
mutation {
  issue8Create(input: {text: "test_1"}) {
    ok
    result {
      id
      text
    }
  }
}
"""

gql_2 = """
mutation {
  issue8Create(input: {text: "test_2"}) {
    ok
  }
}
"""

gql_3 = """
mutation {
  issue8Update(input: {text: "test_1_bis1"}, where: {id: {exact: 1}}) {
    ok
    result {
      id
      text
    }
  }
}
"""

gql_4 = """
mutation {
  issue8Update(input: {text: "test_1_bis2"}, where: {id: {exact: 1}}) {
    ok
  }
}
"""

class Issue8Test(GraphQLTestCase, VerifyResponseAssertionMixins):

    def test_issue_8(self):

        client = Client()

        expected_response = {
            "data": {"issue8Create": {"ok": True, "result": {"text": "test_1"}}}
        }
        response = client.query(gql_1).json()
        self.verify_response(response, expected_response)

        expected_response = {"data": {"issue8Create": {"ok": True}}}
        response = client.query(gql_2).json()
        self.verify_response(response, expected_response)

        expected_response = {
            "data": {"issue8Update": {"ok": True, "result": {"id": "1", "text": "test_1_bis1"}}}
        }
        response = client.query(gql_3).json()
        self.verify_response(response, expected_response)

        expected_response = {
            "data": {"issue8Update": {"ok": True}}
        }
        response = client.query(gql_4).json()
        self.verify_response(response, expected_response)
