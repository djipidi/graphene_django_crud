# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins

MUTATION_CREATE_TEST_A = """
mutation personCreate ($input: PersonCreateInput!) {
  personCreate(input:$input){
    ok
    errors{field,messages}
    result {
      id, name
      childs {
        data {
          id, name
        }
      }
      father {
        id, name
      }
      friends {
        data {
          id, name
        }
      }
    }
  }
}
"""

class RelationTest(GraphQLTestCase, VerifyResponseAssertionMixins):
  def test_relation(self):

      client = Client()

      variables = {
          "input": {
              "name": "p1",
              "childs": {"create": [{"name": "p2"}, {"name": "p3"}]},
              "father": {
                  "create": {"name": "p4"},
              },
              "friends": {"create": [{"name": "p5"}, {"name": "p6"}]},
          }
      }
      expected_response = {
          "data": {
              "personCreate": {
                  "ok": True,
                  "errors": [],
                  "result": {
                      "name": "p1",
                      "childs": {"data": [{"name": "p2"}, {"name": "p3"}]},
                      "father": {"name": "p4"},
                      "friends": {"data": [{"name": "p5"}, {"name": "p6"}]},
                  },
              }
          }
      }

      response = client.query(MUTATION_CREATE_TEST_A, variables=variables).json()
      self.verify_response(response, expected_response)

      p1_id = response["data"]["personCreate"]["result"]["id"]
      p2_id = response["data"]["personCreate"]["result"]["childs"]["data"][0]["id"]
      p3_id = response["data"]["personCreate"]["result"]["childs"]["data"][1]["id"]
      p4_id = response["data"]["personCreate"]["result"]["father"]["id"]
      p5_id = response["data"]["personCreate"]["result"]["friends"]["data"][0]["id"]
      p6_id = response["data"]["personCreate"]["result"]["friends"]["data"][1]["id"]
