# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from django.contrib.auth.models import User

QUERY_GET_ALL_USERS = '''
query{users{data{id, username}}}
'''
def test_user():
    USER_LEN = 10
    for i in range(USER_LEN):
        u = User(username="user" + str(i), password="Secret.123")
        u.save()

    client = Client()
    response = client.query(QUERY_GET_ALL_USERS).json()
    assert len(response["data"]["users"]["data"]) == USER_LEN


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
def test_relation():

    variable = {
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
    response = client.query(MUTATION_CREATE_TEST_A, variable=variable).json()

    assert response["data"]["personCreate"]["ok"]
    assert len(response["data"]["personCreate"]["result"]["childs"]["data"]) == 2
    assert len(response["data"]["personCreate"]["result"]["friends"]["data"]) == 2
    assert response["data"]["personCreate"]["result"]["father"]["name"] == "root"

