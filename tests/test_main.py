# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from django.contrib.auth.models import User

QUERY_GET_ALL_USERS = '''
query{users{data{id, username}}}
'''

user_fragment = '''
fragment user on UserType {
  id
  username
  password
  firstName
  lastName
  isStaff
  isSuperuser
  groups{
    count
    data{
      id
      name
    }
  }
}
'''
users_gql = user_fragment + '''
query users($where:UserWhereInput) {
  users(where:$where) {
    count
    data{
      ...user
    }
  }
}
'''
userCreate_gql = user_fragment + '''
mutation userCreate($input: UserCreateInput!) {
  userCreate(input: $input) {
    ok
    result {
      ...user
    }
  }
}
'''
userUpdate_gql = user_fragment + '''
mutation userUpdate($input: UserUpdateInput!, $where: UserWhereInput!) {
  userUpdate(input: $input, where:$where) {
    ok
    result {
      ...user
    }
  }
}
'''

group_fragment = '''
fragment group on GroupType {
  id
  name
  userSet {
    count
    data {
      id
      username
      password
      firstName
      lastName
      isStaff
      isSuperuser
    }
  }
}
'''
groupCreate_gql = group_fragment + '''
mutation groupCreate($input: GroupCreateInput!) {
  groupCreate(input: $input) {
    ok
    result {
      ...group
    }
  }
}
'''

groupUdate_gql = group_fragment + '''
mutation groupUpdate($input: GroupUpdateInput!, $where:GroupWhereInput!) {
  groupUpdate(input: $input, where:$where) {
    ok
    result {
      ...group
    }
  }
}
'''


def test_main():
    
    client = Client()

    variables = {
      "input": {
        "name": "g1",
        "userSet": {
          "create": [
            {
              "username": "u1",
              "password": "u1pwd",
              "firstName": "u1fn",
              "lastName": "u1ln"
            },
            {
              "username": "u2",
              "password": "u2pwd",
              "firstName": "u2fn",
              "lastName": "u2ln"
            }
          ]
        }
      }
    }

    response = client.query(groupCreate_gql, variables=variables).json()

    assert response["data"]["groupCreate"]["ok"] == True
    g1_id = response["data"]["groupCreate"]["result"]["id"]
    assert response["data"]["groupCreate"]["result"]["name"] == "g1"
    assert response["data"]["groupCreate"]["result"]["userSet"]["count"] == 2
    assert len(response["data"]["groupCreate"]["result"]["userSet"]["data"]) == 2
    u1_id = response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["id"]
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["username"] == "u1"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["password"] != "u1pwd"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["firstName"] == "u1fn"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["lastName"] == "u1ln"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["isStaff"] == False
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["isSuperuser"] == False
    u2_id = response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["id"]
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["username"] == "u2"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["password"] != "u2pwd"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["firstName"] == "u2fn"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["lastName"] == "u2ln"
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["isStaff"] == False
    assert response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["isSuperuser"] == False

    variables = {
        "input": {
            "username": "u3",
            "password": "u3pwd",
            "firstName": "u3fn",
            "lastName": "u3ln",
            "groups": {
                "connect" : [
                    {"id": {"equals": g1_id}},
                ],
                "create": [
                    {
                        "name": "g2",
                        "userSet": {
                            "connect": [
                                {"id": {"equals": u1_id}},
                                {"id": {"equals": u2_id}}
                            ],
                            "create": [
                                {
                                "username": "u4",
                                "password": "u4pwd",
                                "firstName": "u4fn",
                                "lastName": "u4ln"
                                },
                                {
                                "username": "u5",
                                "password": "u5pwd",
                                "firstName": "u5fn",
                                "lastName": "u5ln"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

    response = client.query(userCreate_gql, variables=variables).json()
    assert response["data"]["userCreate"]["ok"] == True
    u3_id = response["data"]["userCreate"]["result"]["id"]
    assert response["data"]["userCreate"]["result"]["username"] == "u3"
    assert response["data"]["userCreate"]["result"]["password"] != "u3pwd"
    assert response["data"]["userCreate"]["result"]["firstName"] == "u3fn"
    assert response["data"]["userCreate"]["result"]["lastName"] == "u3ln"
    assert response["data"]["userCreate"]["result"]["isStaff"] == False
    assert response["data"]["userCreate"]["result"]["isSuperuser"] == False
    assert response["data"]["userCreate"]["result"]["groups"]["count"] == 2
    assert len(response["data"]["userCreate"]["result"]["groups"]["data"]) == 2
    assert response["data"]["userCreate"]["result"]["groups"]["data"][0]["id"] == g1_id
    assert response["data"]["userCreate"]["result"]["groups"]["data"][0]["name"] == "g1"
    g2_id = response["data"]["userCreate"]["result"]["groups"]["data"][1]["id"]
    assert response["data"]["userCreate"]["result"]["groups"]["data"][1]["name"] == "g2"

    variables= {
        "where": {"id": {"equals": g2_id}
        },
        "input": {
            "name": "g2_update",
            "userSet": {
            "connect": [{"id": {"equals": u2_id}}],
            "disconnect": [{"id": {"equals": u1_id}}],
            "delete": [{"id": {"equals": u3_id}}]
            }
        }
    }
    response = client.query(groupUdate_gql, variables=variables).json()
    assert response["data"]["groupUpdate"]["ok"] == True
    assert response["data"]["groupUpdate"]["result"]["id"] == "2"
    assert response["data"]["groupUpdate"]["result"]["name"] == "g2_update"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["count"] == 3
    assert len(response["data"]["groupUpdate"]["result"]["userSet"]["data"]) == 3
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["id"] == u2_id
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["username"] == "u2"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["password"] != "u2pwd"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["firstName"] == "u2fn"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["lastName"] == "u2ln"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["isStaff"] == False
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["isSuperuser"] == False
    u4_id = response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["id"]
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["username"] == "u4"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["password"] != "u4pwd"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["firstName"] == "u4fn"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["lastName"] == "u4ln"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["isStaff"] == False
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["isSuperuser"] == False
    u5_id = response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["id"]
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["username"] == "u5"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["password"] != "u5pwd"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["firstName"] == "u5fn"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["lastName"] == "u5ln"
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["isStaff"] == False
    assert response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["isSuperuser"] == False

    response = client.query(users_gql).json()

    assert response["data"]["users"]["count"] == 4
    assert len(response["data"]["users"]["data"]) == 4
    assert response["data"]["users"]["data"][0]["id"] == u1_id
    assert response["data"]["users"]["data"][0]["username"] == "u1"
    assert response["data"]["users"]["data"][0]["password"] != "u1pwd"
    assert response["data"]["users"]["data"][0]["firstName"] == "u1fn"
    assert response["data"]["users"]["data"][0]["lastName"] == "u1ln"
    assert response["data"]["users"]["data"][0]["isStaff"] == False
    assert response["data"]["users"]["data"][0]["isSuperuser"] == False
    assert response["data"]["users"]["data"][1]["id"] == u2_id
    assert response["data"]["users"]["data"][1]["username"] == "u2"
    assert response["data"]["users"]["data"][1]["password"] != "u2pwd"
    assert response["data"]["users"]["data"][1]["firstName"] == "u2fn"
    assert response["data"]["users"]["data"][1]["lastName"] == "u2ln"
    assert response["data"]["users"]["data"][1]["isStaff"] == False
    assert response["data"]["users"]["data"][1]["isSuperuser"] == False
    assert response["data"]["users"]["data"][2]["id"] == u4_id
    assert response["data"]["users"]["data"][2]["username"] == "u4"
    assert response["data"]["users"]["data"][2]["password"] != "u4pwd"
    assert response["data"]["users"]["data"][2]["firstName"] == "u4fn"
    assert response["data"]["users"]["data"][2]["lastName"] == "u4ln"
    assert response["data"]["users"]["data"][2]["isStaff"] == False
    assert response["data"]["users"]["data"][2]["isSuperuser"] == False
    assert response["data"]["users"]["data"][3]["id"] == u5_id
    assert response["data"]["users"]["data"][3]["username"] == "u5"
    assert response["data"]["users"]["data"][3]["password"] != "u5pwd"
    assert response["data"]["users"]["data"][3]["firstName"] == "u5fn"
    assert response["data"]["users"]["data"][3]["lastName"] == "u5ln"
    assert response["data"]["users"]["data"][3]["isStaff"] == False
    assert response["data"]["users"]["data"][3]["isSuperuser"] == False
    assert response["data"]["users"]["data"][0]["groups"]["count"] == 1
    assert len(response["data"]["users"]["data"][0]["groups"]["data"]) == 1
    assert response["data"]["users"]["data"][1]["groups"]["count"] == 2
    assert len(response["data"]["users"]["data"][1]["groups"]["data"]) == 2
    assert response["data"]["users"]["data"][2]["groups"]["count"] == 1
    assert len(response["data"]["users"]["data"][2]["groups"]["data"]) == 1
    assert response["data"]["users"]["data"][3]["groups"]["count"] == 1
    assert len(response["data"]["users"]["data"][3]["groups"]["data"]) == 1
    assert response["data"]["users"]["data"][0]["groups"]["data"][0]["id"] == g1_id
    assert response["data"]["users"]["data"][0]["groups"]["data"][0]["name"] == "g1"
    assert response["data"]["users"]["data"][1]["groups"]["data"][0]["id"] == g1_id
    assert response["data"]["users"]["data"][1]["groups"]["data"][0]["name"] == "g1"
    assert response["data"]["users"]["data"][1]["groups"]["data"][1]["id"] == g2_id
    assert response["data"]["users"]["data"][1]["groups"]["data"][1]["name"] == "g2_update"
    assert response["data"]["users"]["data"][2]["groups"]["data"][0]["id"] == g2_id
    assert response["data"]["users"]["data"][2]["groups"]["data"][0]["name"] == "g2_update"
    assert response["data"]["users"]["data"][3]["groups"]["data"][0]["id"] == g2_id
    assert response["data"]["users"]["data"][3]["groups"]["data"][0]["name"] == "g2_update"

    variables = {"where": {"groups": {"id": {"equals": g2_id}}}}

    response = client.query(users_gql, variables=variables).json()

    assert response["data"]["users"]["count"] == 3
    assert len(response["data"]["users"]["data"]) == 3
    assert response["data"]["users"]["data"][0]["id"] == u2_id
    assert response["data"]["users"]["data"][0]["username"] == "u2"
    assert response["data"]["users"]["data"][0]["password"] != "u2pwd"
    assert response["data"]["users"]["data"][0]["firstName"] == "u2fn"
    assert response["data"]["users"]["data"][0]["lastName"] == "u2ln"
    assert response["data"]["users"]["data"][0]["isStaff"] == False
    assert response["data"]["users"]["data"][0]["isSuperuser"] == False
    assert response["data"]["users"]["data"][1]["id"] == u4_id
    assert response["data"]["users"]["data"][1]["username"] == "u4"
    assert response["data"]["users"]["data"][1]["password"] != "u4pwd"
    assert response["data"]["users"]["data"][1]["firstName"] == "u4fn"
    assert response["data"]["users"]["data"][1]["lastName"] == "u4ln"
    assert response["data"]["users"]["data"][1]["isStaff"] == False
    assert response["data"]["users"]["data"][1]["isSuperuser"] == False
    assert response["data"]["users"]["data"][2]["id"] == u5_id
    assert response["data"]["users"]["data"][2]["username"] == "u5"
    assert response["data"]["users"]["data"][2]["password"] != "u5pwd"
    assert response["data"]["users"]["data"][2]["firstName"] == "u5fn"
    assert response["data"]["users"]["data"][2]["lastName"] == "u5ln"
    assert response["data"]["users"]["data"][2]["isStaff"] == False
    assert response["data"]["users"]["data"][2]["isSuperuser"] == False
    assert response["data"]["users"]["data"][0]["groups"]["count"] == 2
    assert len(response["data"]["users"]["data"][0]["groups"]["data"]) == 2
    assert response["data"]["users"]["data"][1]["groups"]["count"] == 1
    assert len(response["data"]["users"]["data"][1]["groups"]["data"]) == 1
    assert response["data"]["users"]["data"][2]["groups"]["count"] == 1
    assert len(response["data"]["users"]["data"][2]["groups"]["data"]) == 1
    assert response["data"]["users"]["data"][0]["groups"]["data"][0]["id"] == g1_id
    assert response["data"]["users"]["data"][0]["groups"]["data"][0]["name"] == "g1"
    assert response["data"]["users"]["data"][0]["groups"]["data"][1]["id"] == g2_id
    assert response["data"]["users"]["data"][0]["groups"]["data"][1]["name"] == "g2_update"
    assert response["data"]["users"]["data"][1]["groups"]["data"][0]["id"] == g2_id
    assert response["data"]["users"]["data"][1]["groups"]["data"][0]["name"] == "g2_update"
    assert response["data"]["users"]["data"][2]["groups"]["data"][0]["id"] == g2_id
    assert response["data"]["users"]["data"][2]["groups"]["data"][0]["name"] == "g2_update"

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

