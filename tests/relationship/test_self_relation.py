# -*- coding: utf-8 -*-
import pytest
from tests.client import Client

MUTATION_CREATE_TEST_A = '''
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
'''
def test_relation_old():

    variables = {
      "input" : {
        "name": "A",
        "childs" : {
          "create" : [
            {"name" : "AA"},
            {"name" : "AB"}
          ]
        },
        "father" : {
          "create" : {"name" : "root"},
        },
        "friends" : {
          "create" : [
            {"name" : "B"},
            {"name" : "C"}
          ]
        }
      }
    }

    client = Client()
    response = client.query(MUTATION_CREATE_TEST_A, variables=variables).json()

    assert response["data"]["personCreate"]["ok"]
    assert len(response["data"]["personCreate"]["result"]["childs"]["data"]) == 2
    assert len(response["data"]["personCreate"]["result"]["friends"]["data"]) == 2
    assert response["data"]["personCreate"]["result"]["father"]["name"] == "root"

